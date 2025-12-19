import os
import zipfile

def create_resource_pack():
    # Configuration
    # You can manually set your version name here
    version_tag = "v1.0.0" 
    zip_name = f"Shulker Labels [{version_tag}].zip"
    
    # Files and directories to exclude from the ZIP
    exclude = {
        ".git", 
        ".github", 
        "build.py", 
        "custom_definitions.json", 
        ".gitignore", 
        "block_models.json", 
        "item_models.json", 
        "scan.py",
        "pack.py",
        zip_name # Don't include the zip inside itself
    }

    print(f"Starting build for {zip_name}...")

    # Optional: Run your build script if it generates files needed for the zip
    if os.path.exists("build.py"):
        print("Executing build.py...")
        os.system("python build.py")

    print("Packing files...")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude]
            
            for file in files:
                if file not in exclude:
                    # Construct the full local path
                    file_path = os.path.join(root, file)
                    
                    # Construct the path inside the ZIP (relative to current dir)
                    archive_name = os.path.relpath(file_path, '.')
                    
                    zipf.write(file_path, archive_name)
                    # print(f"  + Added: {archive_name}")

    print("-" * 30)
    print(f"Successfully created: {zip_name}")

if __name__ == "__main__":
    create_resource_pack()