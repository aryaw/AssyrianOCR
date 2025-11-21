from argostranslate import package, translate

FROM = "en"
TO = "id"

print("Checking available Argos Translate models...\n")

available_packages = package.get_available_packages()

target_pkg = None
for p in available_packages:
    if p.from_code == FROM and p.to_code == TO:
        target_pkg = p
        break

if not target_pkg:
    print(f"EN -> ID model NOT FOUND in registry")
    exit(1)

print(f"Found model: {target_pkg.from_name} -> {target_pkg.to_name}")

print("Downloading model...")
download_path = target_pkg.download()
print(f"   Downloaded to: {download_path}")

print("Installing model...")
package.install_from_path(download_path)

print("Loading installed languages...")
translate.load_installed_languages()

print("Argos Translate EN -> ID model installed successfully!")