def load_labels(path):
    list = []
    with open(path, 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
        
        for line in lines:
            list.append(line)
    return list

if __name__ == '__main__':
  print(load_labels("age-labels.txt"))