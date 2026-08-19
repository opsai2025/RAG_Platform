from pathlib import Path
path = Path('/mnt/data/app-(4).py')
text = path.read_text(encoding='utf-8')
lines = text.splitlines()
# Find ask_rag and target lines
start = None
for i, line in enumerate(lines):
    if 'def ask_rag' in line:
        start = i
        break
print('ask_rag starts at line', start+1 if start is not None else None)
# show a window around the function to identify target lines
if start is not None:
    for j in range(max(0, start-5), min(len(lines), start+40)):
        print(f'{j+1}: {lines[j]}')

old = """    response = llm.invoke(prompt)
    return response.content, docs"""
new = """    response = llm.invoke(prompt)
    # مطمئن شو answer یه رشته خالص است
    raw = response.content
    if isinstance(raw, str):
        answer = raw
    elif isinstance(raw, list):
        # بعضی مدل‌ها لیستی از بلوک‌های محتوا برمی‌گردونند
        answer = \" \\".join(
            part.get(\"text\", \"\") if isinstance(part, dict) else str(part)
            for part in raw
        )
    else:
        # fallback برای AIMessage و ساختارهای دیگر
        answer = getattr(raw, \"text\", None) or str(raw)
    return answer, docs"""
if old not in text:
    raise SystemExit('Target snippet not found')
text2 = text.replace(old, new, 1)
path.write_text(text2, encoding='utf-8')
print('\n--- modified excerpt lines 710-730 ---')
new_lines = text2.splitlines()
for j in range(709, min(len(new_lines), 730)):
    print(f'{j+1}: {new_lines[j]}')
print('\nSaved to', path)
