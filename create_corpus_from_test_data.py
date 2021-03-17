def create_document(filename, content):
    with open(f'/corpus/{filename}', 'w') as f:
        f.write(content)

with open("test_data/TIME.ALL") as f:
    text_num = 0
    content = ''
    for line in f:
        if line.startswith('*TEXT'):
            create_document(f'text_{text_num}.txt', content)
            text_num = line.split()[1]
            content = ''

        elif line.startswith('*STOP'):
            create_document(f'text_{text_num}.txt', content)

        else:
            content += line  