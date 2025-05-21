import os
import yaml

def save_test_cases_as_yaml(test_cases):
    """
    Save test cases as YAML files in appropriate directories based on the 'page' attribute.
    If 'page' is not specified, save to a default location.
    """
    for i, test_case in enumerate(test_cases):
        # Convert test case to dictionary for YAML serialization
        test_dict = {
            "name": test_case.name,
            "task": test_case.task,
            "expected_result": test_case.expected_result,
            "steps": test_case.steps
        }
        
        # Get page or use default
        page = getattr(test_case, 'page', 'general')
        
        # Create directory structure
        dir_path = f"pages/{page}"
        os.makedirs(dir_path, exist_ok=True)
        
        # Create filename (use sanitized test name or index)
        filename = f"{i+1}_{test_case.name.lower().replace(' ', '_')}.yaml"
        file_path = f"{dir_path}/{filename}"
        
        # Write YAML file
        with open(file_path, 'w') as f:
            yaml.dump(test_dict, f, default_flow_style=False, sort_keys=False)
        
        print(f"Created test file: {file_path}")