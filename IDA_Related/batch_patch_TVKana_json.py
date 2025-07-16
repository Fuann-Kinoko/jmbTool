import idc
import ida_bytes
import idaapi
import ida_kernwin
import json
import os

def find_symbol_address(symbol_name):
    """Find address of symbol in IDA's namelist"""
    for i in range(idaapi.get_nlist_size()):
        name = idaapi.get_nlist_name(i)
        if name and name == symbol_name:  # Exact match
            return idaapi.get_nlist_ea(i)
    return idaapi.BADADDR

def replace_string_with_padding(address, new_string):
    """Safely replace string at address with proper null-termination and padding"""
    if address == idaapi.BADADDR:
        return False

    # Get original string length (until null byte)
    orig_length = 0
    while ida_bytes.get_byte(address + orig_length) != 0:
        orig_length += 1

    # Calculate total allocated space (including padding)
    total_space = orig_length
    while ida_bytes.get_byte(address + total_space) == 0:
        total_space += 1

    # Convert to UTF-8
    try:
        new_bytes = new_string.encode('utf-8')
    except UnicodeEncodeError:
        print(f"Unicode encode error for string: {new_string}")
        return False

    # Validate length
    if len(new_bytes) > total_space:
        print(f"String too long (max {total_space} bytes): {new_string}")
        return False

    # Patch the string
    for i in range(len(new_bytes)):
        ida_bytes.patch_byte(address + i, new_bytes[i])

    # Null terminate
    ida_bytes.patch_byte(address + len(new_bytes), 0)

    # Zero-fill remainder
    for i in range(len(new_bytes) + 1, total_space):
        ida_bytes.patch_byte(address + i, 0)

    return True

def load_translation_file(file_path):
    """Load and validate translation JSON file"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            if not isinstance(data, dict):
                print("Error: JSON root should be a dictionary")
                return None

            return data
    except Exception as e:
        print(f"Error loading JSON: {str(e)}")
        return None

def batch_replace_strings(translation_dict):
    """Process all translations in the dictionary"""
    success_count = 0
    skip_count = 0
    fail_count = 0

    for symbol_name, new_string in translation_dict.items():
        address = find_symbol_address(symbol_name)

        if address == idaapi.BADADDR:
            print(f"Symbol not found: {symbol_name}")
            fail_count += 1
            continue

        if replace_string_with_padding(address, new_string):
            print(f"Patched: {symbol_name} -> {new_string}")
            success_count += 1
        else:
            print(f"Failed to patch: {symbol_name}")
            skip_count += 1

    print(f"\nResults: {success_count} successful, {skip_count} skipped, {fail_count} failed")

def main(default_path):
    # Ask for JSON file path
    json_path = default_path
    if not json_path:
        return

    # Load translation data
    translation_dict = load_translation_file(json_path)
    if not translation_dict:
        return

    # Confirm before proceeding
    count = len(translation_dict)
    if not ida_kernwin.ask_yn(ida_kernwin.ASKBTN_YES,
                            f"Found {count} translations. Proceed with patching?"):
        return

    # Execute batch replacement
    batch_replace_strings(translation_dict)

if __name__ == '__main__':
    tvkana_path = r"D:/SteamLibrary/steamapps/common/killer7/Tools/jmbDump/assets/translation/TVKana.json"
    tvkana_menu_path = r"D:/SteamLibrary/steamapps/common/killer7/Tools/jmbDump/assets/translation/TVKana_Menu.json"
    main(tvkana_path)
    main(tvkana_menu_path)