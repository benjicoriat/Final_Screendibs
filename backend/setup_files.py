import os

# Create all necessary directories
directories = [
    "app/core",
    "app/models",
    "app/routes",
    "app/services",
    "app/utils"
]

for dir_path in directories:
    os.makedirs(dir_path, exist_ok=True)
    init_file = os.path.join(dir_path, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write("")
        print(f"Created {init_file}")

# Create app/__init__.py
app_init = "app/__init__.py"
if not os.path.exists(app_init):
    with open(app_init, 'w') as f:
        f.write("")
    print(f"Created {app_init}")

print("\nAll __init__.py files created!")
print("\nNow manually create these files with the code I provided:")
print("- app/models/user.py")
print("- app/models/payment.py")
print("- app/models/schemas.py")
print("- app/core/config.py")
print("- app/core/database.py")
print("- app/core/security.py")
print("- app/routes/auth.py")
print("- app/routes/books.py")
print("- app/routes/payments.py")
print("- app/services/book_search.py")
print("- app/services/report_generator.py")
print("- app/services/email_service.py")
print("- app/utils/auth.py")
print("- app/main.py")

