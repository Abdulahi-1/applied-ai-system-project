"""
Unit tests for models/schemas.py and agent/tools.py.
No Gemini API key is required to run these tests.
"""

import pytest
from models.schemas import Task, Pet, Owner, Schedule
from agent.tools import SchedulerTools


# ================================================================== Task tests

class TestTask:
    def test_defaults(self):
        task = Task(task_type="Walk", duration_minutes=30, priority=5)
        assert not task.is_completed
        assert task.notes == ""

    def test_complete(self):
        task = Task(task_type="Walk", duration_minutes=30, priority=5)
        task.complete()
        assert task.is_completed

    def test_is_high_priority_boundary(self):
        assert Task("A", 10, 8).is_high_priority()
        assert Task("A", 10, 10).is_high_priority()
        assert not Task("A", 10, 7).is_high_priority()

    def test_get_summary_pending(self):
        task = Task(task_type="Feed", duration_minutes=10, priority=9)
        summary = task.get_summary()
        assert "Feed" in summary
        assert "10" in summary
        assert "⏳" in summary

    def test_get_summary_completed(self):
        task = Task(task_type="Feed", duration_minutes=10, priority=9)
        task.complete()
        assert "✅" in task.get_summary()

    def test_to_dict_keys(self):
        task = Task(task_type="Groom", duration_minutes=20, priority=6, notes="brush")
        d = task.to_dict()
        assert set(d.keys()) == {
            "task_type", "duration_minutes", "priority", "notes", "is_completed"
        }


# ================================================================== Schedule tests

class TestSchedule:
    def _make_schedule(self, budget: int = 60) -> Schedule:
        owner = Owner(name="Alice", email="", available_minutes=budget)
        pet = Pet(name="Buddy", breed="Lab", size="large", species="dog", age_years=3)
        return Schedule(owner=owner, pet=pet)

    def test_add_and_count(self):
        s = self._make_schedule()
        s.add_task(Task("Walk", 30, 8))
        s.add_task(Task("Feed", 10, 9))
        assert len(s.tasks) == 2

    def test_remove_task(self):
        s = self._make_schedule()
        s.add_task(Task("Walk", 30, 8))
        removed = s.remove_task("Walk")
        assert removed == 1
        assert len(s.tasks) == 0

    def test_remove_nonexistent(self):
        s = self._make_schedule()
        assert s.remove_task("Nonexistent") == 0

    def test_get_total_duration(self):
        s = self._make_schedule()
        s.add_task(Task("Walk", 30, 8))
        s.add_task(Task("Feed", 15, 9))
        assert s.get_total_duration() == 45

    def test_generate_plan_sorted(self):
        s = self._make_schedule()
        s.add_task(Task("Low", 10, 2))
        s.add_task(Task("High", 10, 9))
        s.add_task(Task("Mid", 10, 5))
        plan = s.generate_plan()
        priorities = [t.priority for t in plan]
        assert priorities == sorted(priorities, reverse=True)

    def test_is_over_budget_false(self):
        s = self._make_schedule(budget=60)
        s.add_task(Task("Walk", 30, 8))
        assert not s.is_over_budget()

    def test_is_over_budget_true(self):
        s = self._make_schedule(budget=20)
        s.add_task(Task("Walk", 30, 8))
        assert s.is_over_budget()

    def test_check_conflicts_over_budget(self):
        s = self._make_schedule(budget=10)
        s.add_task(Task("Walk", 30, 8))
        warnings = s.check_conflicts()
        assert any("over budget" in w.lower() for w in warnings)

    def test_check_conflicts_duplicate(self):
        s = self._make_schedule()
        s.add_task(Task("Walk", 10, 5))
        s.add_task(Task("Walk", 10, 5))
        warnings = s.check_conflicts()
        assert any("Duplicate" in w for w in warnings)

    def test_check_conflicts_all_done(self):
        s = self._make_schedule()
        t = Task("Walk", 10, 5)
        t.complete()
        s.add_task(t)
        warnings = s.check_conflicts()
        assert any("completed" in w.lower() for w in warnings)

    def test_check_conflicts_clean(self):
        s = self._make_schedule(budget=120)
        s.add_task(Task("Walk", 30, 8))
        s.add_task(Task("Feed", 10, 9))
        assert s.check_conflicts() == []

    def test_explain_plan_within_budget(self):
        s = self._make_schedule(budget=60)
        s.add_task(Task("Walk", 30, 8))
        assert "spare" in s.explain_plan()

    def test_explain_plan_over_budget(self):
        s = self._make_schedule(budget=10)
        s.add_task(Task("Walk", 30, 8))
        assert "exceeds" in s.explain_plan()


# ================================================================== SchedulerTools tests

class TestSchedulerTools:
    def _make_tools(self, budget: int = 120) -> SchedulerTools:
        return SchedulerTools(
            owner_name="Bob",
            pet_name="Mochi",
            available_minutes=budget,
        )

    def test_add_task_success(self):
        tools = self._make_tools()
        result = tools.add_task("Walk", 30, 8)
        assert "Added" in result
        assert len(tools.schedule.tasks) == 1

    def test_add_task_bad_priority(self):
        tools = self._make_tools()
        result = tools.add_task("Walk", 30, 11)
        assert "Error" in result
        assert len(tools.schedule.tasks) == 0

    def test_add_task_bad_duration(self):
        tools = self._make_tools()
        result = tools.add_task("Walk", 0, 5)
        assert "Error" in result

    def test_remove_task_exists(self):
        tools = self._make_tools()
        tools.add_task("Walk", 30, 8)
        result = tools.remove_task("Walk")
        assert "Removed" in result
        assert len(tools.schedule.tasks) == 0

    def test_remove_task_missing(self):
        tools = self._make_tools()
        result = tools.remove_task("Ghost")
        assert "No task" in result

    def test_list_tasks_empty(self):
        tools = self._make_tools()
        assert "No tasks" in tools.list_tasks()

    def test_list_tasks_json(self):
        import json
        tools = self._make_tools()
        tools.add_task("Feed", 10, 9)
        data = json.loads(tools.list_tasks())
        assert data[0]["task_type"] == "Feed"

    def test_get_schedule_empty(self):
        tools = self._make_tools()
        assert "No tasks" in tools.get_schedule()

    def test_get_schedule_ordered(self):
        tools = self._make_tools()
        tools.add_task("Low", 10, 1)
        tools.add_task("High", 10, 9)
        lines = tools.get_schedule().splitlines()
        assert "High" in lines[0]

    def test_check_conflicts_clean(self):
        tools = self._make_tools(budget=120)
        tools.add_task("Walk", 30, 8)
        assert "No conflicts" in tools.check_conflicts()

    def test_check_conflicts_over_budget(self):
        tools = self._make_tools(budget=10)
        tools.add_task("Walk", 30, 8)
        assert "budget" in tools.check_conflicts().lower()

    def test_complete_task(self):
        tools = self._make_tools()
        tools.add_task("Feed", 10, 9)
        result = tools.complete_task("Feed")
        assert "Marked" in result
        assert tools.schedule.tasks[0].is_completed

    def test_complete_task_missing(self):
        tools = self._make_tools()
        result = tools.complete_task("Ghost")
        assert "No task" in result

    def test_get_summary_contains_owner(self):
        tools = self._make_tools()
        summary = tools.get_summary()
        assert "Bob" in summary
        assert "Mochi" in summary

    def test_reset_schedule(self):
        tools = self._make_tools()
        tools.add_task("Walk", 30, 8)
        tools.add_task("Feed", 10, 9)
        result = tools.reset_schedule()
        assert "2" in result
        assert len(tools.schedule.tasks) == 0

    def test_dispatch_valid(self):
        tools = self._make_tools()
        result = tools.dispatch("add_task", {"task_type": "Groom", "duration_minutes": 20, "priority": 7})
        assert "Added" in result

    def test_dispatch_invalid(self):
        tools = self._make_tools()
        result = tools.dispatch("fly_to_moon", {})
        assert "Unknown tool" in result
