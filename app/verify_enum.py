from models.project import ProjectStatusEnum
print("VERIFICATION_OUTPUT_START")
for member in ProjectStatusEnum:
    print(f"Key: {member.name}, Value: {member.value!r}")
print("VERIFICATION_OUTPUT_END")
