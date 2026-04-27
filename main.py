"Import classes from pawpal_system.py to test the functionality of the PawPal system."
from pawpal_system import Pet, CareTask, Owner, DailyScheduler
def main():
    # Create an owner
    user = Owner(name="Alice", email="alice@example.com", available_minutes=120)
    # Create 2 pets
    pet = Pet(name="Buddy", breed="Golden Retriever", size="Large", species="Dog", age_years=3)
    pet2 = Pet(name="Mittens", breed="Siamese", size="Small", species="Cat", age_years=2)
    # Add pets to the user
    user.add_pet(pet)
    user.add_pet(pet2)
    # Create a care task
    task = CareTask(task_type="Feeding", duration_minutes=10, priority=5)
    # Create a PawPal system instance
    pawpal_system = DailyScheduler(owner=user, pet=pet)
    # Adds at least three Tasks with different times to those pets.
    task2 = CareTask(task_type="Grooming", duration_minutes=20, priority=7)
    task3 = CareTask(task_type="Exercise", duration_minutes=15, priority=9)
    task_duplicate = CareTask(task_type="Feeding", duration_minutes=10, priority=5)  # duplicate of task
    pawpal_system.add_task(task)
    pawpal_system.add_task(task2)
    pawpal_system.add_task(task3)
    pawpal_system.add_task(task_duplicate)

    # Check for conflicts before generating the plan.
    conflicts = pawpal_system.check_conflicts()
    if conflicts:
        print("Warnings:")
        for warning in conflicts:
            print(f"  [!] {warning}")

    # Print a "Today's Schedule" to the terminal.
    print("\nToday's Schedule:")
    for task in pawpal_system.generate_plan():
        print(task.get_summary())

if __name__ == "__main__":
    main()