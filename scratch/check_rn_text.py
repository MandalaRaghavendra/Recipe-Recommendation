import os
import re

src_dir = r"d:\recipie\Recipe-Recommendation\mobile-app"
suspicious = []

for root, dirs, files in os.walk(src_dir):
    if "node_modules" in root or ".expo" in root:
        continue
    for file in files:
        if file.endswith(".js"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()

            # Look for patterns like:
            # 1. >some_text< outside of <Text>
            # 2. {var && <View
            # 3. {count && <
            for idx, line in enumerate(lines):
                # Pattern: {something && <
                matches = re.finditer(r'\{([^}]+)&&\s*<', line)
                for m in matches:
                    expr = m.group(1).strip()
                    if not (expr.startswith("!") or "===" in expr or "!==" in expr or ">" in expr or "<" in expr or "Boolean(" in expr):
                        suspicious.append((file, idx + 1, f"Possible non-boolean &&: {{{expr} && <}}"))

                # Pattern: text directly between tags that are not <Text>
                # e.g., <View>text</View> or <TouchableOpacity>text</TouchableOpacity>
                view_text = re.finditer(r'<(View|TouchableOpacity|ScrollView|SafeAreaView)[^>]*>([^<{]+)<', line)
                for m in view_text:
                    txt = m.group(2).strip()
                    if txt and not txt.startswith("//") and not txt.startswith("/*"):
                        suspicious.append((file, idx + 1, f"Direct text inside <{m.group(1)}>: '{txt}'"))

print(f"Found {len(suspicious)} potential issues:")
for f, l, msg in suspicious:
    print(f"{f}:{l}: {msg}")
