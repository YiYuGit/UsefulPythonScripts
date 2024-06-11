#Read windows registry, compare the read value with user provided value.

import winreg

def read_registry_value(key_path, value_name):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        value, value_type = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        return value
    except FileNotFoundError:
        print(f"Registry key '{key_path}' not found.")
        return None
    except Exception as e:
        print(f"Error reading registry value: {str(e)}")
        return None

if __name__ == "__main__":
    registry_key_path = r"Computer\HKEY_CURRENT_USER\EUDC\932\SystemDefaultEUDCFont"
    value_name = "SystemDefaultEUDCFont"

    registry_value = read_registry_value(registry_key_path, value_name)
    print (registry_value)
    
    if registry_value is not None:
        # Compare the registry value with some preset values
        if registry_value == "YourPresetValue":
            print("Registry value matches preset value.")
        else:
            print("Registry value does not match preset value.")
    else:
        print("Registry value not found.")
