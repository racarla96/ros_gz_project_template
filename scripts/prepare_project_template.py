import yaml
import os
import sys

def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def list_and_rename_folders(directory, config):
    suffixes = ["_application", "_bringup", "_description", "_gazebo"]
    renamed_folders = []

    # List the folders in the specified directory
    for folder_name in os.listdir(directory):
        full_path = os.path.join(directory, folder_name)
        # Check if it is a folder and if its name starts with 'ros_gz_example_'
        if os.path.isdir(full_path) and folder_name.startswith('ros_gz_example_'):
            for suffix in suffixes:
                if folder_name.endswith(suffix):
                    # Create the new name for the folder
                    new_folder_name = config['project_name'] + suffix
                    new_full_path = os.path.join(directory, new_folder_name)
                    # Rename the folder
                    os.rename(full_path, new_full_path)
                    renamed_folders.append(new_full_path)
                    print(f"Renamed: {full_path} -> {new_full_path}")
                    break
        else:
            print(f"Not renamed: {full_path}")
    return renamed_folders

def modify_file_content(file_path, old_prefix, new_prefix):
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        modified_content = content.replace(old_prefix, new_prefix)
        with open(file_path, 'w') as file:
            file.write(modified_content)
        print(f"Modified: {file_path}")
    else:
        print(f"File not found: {file_path}")

def modify_cmakelists_in_folders(folders, old_prefix, new_prefix):
    for folder in folders:
        cmake_file = os.path.join(folder, 'CMakeLists.txt')
        modify_file_content(cmake_file, old_prefix, new_prefix)

def modify_packagexml_in_folders(folders, config):
    suffixes = ["_application", "_bringup", "_description", "_gazebo"]
    for folder in folders:
        package_file = os.path.join(folder, 'package.xml')
        if os.path.isfile(package_file):
            with open(package_file, 'r') as file:
                content = file.read()

            # Modify specific fields in package.xml
            for suffix in suffixes:
                if folder.endswith(suffix):
                    new_name = f"{config['project_name']}{suffix}"
                    break
            modified_content = content.replace('<name>ros_gz_example_', f'<name>{config["project_name"]}_')
            modified_content = modified_content.replace('<version>0.0.0</version>', f'<version>{config["version"]}</version>')
            modified_content = modified_content.replace('<description>Application-specific implementations for the ros_gz_project example</description>',
                                                        f'<description>Application-specific implementations for the {config["description"]} example</description>')
            modified_content = modified_content.replace('<description>Contains launch files for the ros_gz_example project</description>',
                                                        f'<description>Contains launch files for the {config["description"]} project</description>')
            modified_content = modified_content.replace('<description>SDFormat description files for the ros_gz_example project</description>',
                                                        f'<description>SDFormat description files for the {config["description"]} project</description>')
            modified_content = modified_content.replace('<description>Gazebo-specific implementations for the ros_gz_example project</description>',
                                                        f'<description>Gazebo-specific implementations for the {config["description"]} project</description>')
            modified_content = modified_content.replace('<maintainer email="michael@openrobotics.org">Michael Carroll</maintainer>',
                                                        f'<maintainer email="{config["email"]}">{config["author"]}</maintainer>')
            modified_content = modified_content.replace('<author>Michael Carroll</author>', f'<author>{config["author"]}</author>')
            modified_content = modified_content.replace('  <author>Dharini Dutia</author>', f'')

            modified_content = modified_content.replace('<depend>ros_gz_example_description</depend>', f'<depend>{config["project_name"]}_description</depend>')
            modified_content = modified_content.replace('<depend>ros_gz_example_gazebo</depend>', f'<depend>{config["project_name"]}_gazebo</depend>')

            with open(package_file, 'w') as file:
                file.write(modified_content)

            print(f"Modified package.xml in: {package_file}")
        else:
            print(f"No package.xml found in: {folder}")


def rename_and_modify_additional_files(folders, old_prefix, new_prefix):
    for folder in folders:
        # Handle ros_gz_example_bridge.yaml in ros_gz_example_bringup/config
        if folder.endswith('_bringup'):
            config_folder = os.path.join(folder, 'config')
            old_file = os.path.join(config_folder, 'ros_gz_example_bridge.yaml')
            if os.path.isfile(old_file):
                new_file = os.path.join(config_folder, f'{new_prefix}bridge.yaml')
                os.rename(old_file, new_file)
                modify_file_content(new_file, old_prefix, new_prefix)
        
        # Handle files in ros_gz_example_description/hooks
        if folder.endswith('_description'):
            hooks_folder = os.path.join(folder, 'hooks')
            for filename in ['ros_gz_example_description.dsv.in', 'ros_gz_example_description.sh.in']:
                old_file = os.path.join(hooks_folder, filename)
                if os.path.isfile(old_file):
                    new_file = os.path.join(hooks_folder, filename.replace('ros_gz_example_', new_prefix))
                    os.rename(old_file, new_file)
                    modify_file_content(new_file, old_prefix, new_prefix)
        
        # Handle files in ros_gz_example_gazebo/hooks
        if folder.endswith('_gazebo'):
            hooks_folder = os.path.join(folder, 'hooks')
            for filename in ['ros_gz_example_gazebo.dsv.in', 'ros_gz_example_gazebo.sh.in']:
                old_file = os.path.join(hooks_folder, filename)
                if os.path.isfile(old_file):
                    new_file = os.path.join(hooks_folder, filename.replace('ros_gz_example_', new_prefix))
                    os.rename(old_file, new_file)
                    modify_file_content(new_file, old_prefix, new_prefix)


def modify_launch_files(folders, old_package_names, new_package_names):
    for folder in folders:
        if folder.endswith('_bringup'):
            launch_folder = os.path.join(folder, 'launch')
            for filename in os.listdir(launch_folder):
                if filename.endswith('.launch.py'):
                    launch_file = os.path.join(launch_folder, filename)
                    modify_file_content(launch_file, old_package_names, new_package_names)


if __name__ == "__main__":
    file = sys.argv[0]
    pathname = os.path.dirname(os.path.abspath(__file__))
    yaml_file = 'project_information.yaml'  # Specify the YAML file
    config = read_yaml_file(pathname + "/" + yaml_file)

    directory = "./"  # Specify the directory where the folders are located
    old_prefix = 'ros_gz_example_'
    new_prefix = config['project_name'] + '_'

    renamed_folders = list_and_rename_folders(directory, config)
    modify_cmakelists_in_folders(renamed_folders, old_prefix, new_prefix)
    modify_packagexml_in_folders(renamed_folders, config)
    rename_and_modify_additional_files(renamed_folders, old_prefix, new_prefix)
    modify_launch_files(renamed_folders, old_prefix, new_prefix)