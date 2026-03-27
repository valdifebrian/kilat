"""
KILAT v0.0.2 - SUPER SIMPLE TEST
Test if input() works at all
"""

print("="*60)
print("KILAT Input Test")
print("="*60)

print("\nTest 1: Simple input")
try:
    name = input("What's your name? ")
    print(f"Hello {name}!")
except Exception as e:
    print(f"FAILED: {e}")

print("\nTest 2: Another input")
try:
    task = input("What to do? ")
    print(f"Task: {task}")
except Exception as e:
    print(f"FAILED: {e}")

print("\nTest 3: Loop input")
for i in range(3):
    try:
        text = input(f"Input {i+1}: ")
        print(f"  You said: {text}")
    except Exception as e:
        print(f"  FAILED: {e}")

print("\n✅ All tests completed!")
print("Press Enter to exit...")
# Don't call input() here to avoid blocking in automated tests
# input()
