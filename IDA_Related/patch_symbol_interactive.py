import idc
import ida_bytes
import idaapi
import ida_kernwin

def find_symbol_address(symbol_name):
    # Search through all names in IDA's namelist
    for i in range(idaapi.get_nlist_size()):
        name = idaapi.get_nlist_name(i)
        if name and symbol_name in name:
            return idaapi.get_nlist_ea(i)
    return idaapi.BADADDR

def replace_string_with_padding(address, new_string):
    if address == idaapi.BADADDR:
        print("Error: Symbol not found")
        return False

    # Get the original string length by counting until null byte
    orig_length = 0
    while ida_bytes.get_byte(address + orig_length) != 0:
        orig_length += 1

    # Calculate total allocated space (including null terminator and padding)
    total_space = orig_length
    while ida_bytes.get_byte(address + total_space) == 0:
        total_space += 1

    # Convert new string to UTF-8 bytes
    new_bytes = new_string.encode('utf-8')

    # Check if new string is too long
    if len(new_bytes) > total_space:
        print(f"Error: New string is too long. Max length is {total_space} bytes.")
        return False

    # Patch the new string
    for i in range(len(new_bytes)):
        ida_bytes.patch_byte(address + i, new_bytes[i])

    # Null terminate
    ida_bytes.patch_byte(address + len(new_bytes), 0)

    # Zero out remaining bytes
    for i in range(len(new_bytes) + 1, total_space):
        ida_bytes.patch_byte(address + i, 0)

    print(f"Successfully replaced string at 0x{address:X}")
    return True

# Interactive version
symbol_name = ida_kernwin.ask_str("", 0, "Enter symbol name to replace")
if symbol_name:
    new_string = ida_kernwin.ask_str("", 0, "Enter new string")
    if new_string:
        address = find_symbol_address(symbol_name)
        if address != idaapi.BADADDR:
            replace_string_with_padding(address, new_string)
        else:
            print(f"Error: Symbol '{symbol_name}' not found in namelist")
    else:
        print(f"Error: Please give correct new_string!")
else:
    print(f"Error: Please give correct symbol_name!")