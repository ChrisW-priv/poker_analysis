from os.path import getsize


def find_element_index_in_file(file, element):
    file.seek(0)
    len_of_line = len(file.readline()) + 1
    n_of_lines = getsize(file.name) // len_of_line
    begin = 0
    end = n_of_lines
    while True:
        middle = (begin+end)//2
        number_to_start_from = middle*len_of_line
        file.seek(number_to_start_from)
        middle_line = (file.read(len_of_line-2))
        print(element, middle_line, begin, middle, end)
        if int(middle_line) == element:
            return middle
        elif int(middle_line) < element:
            begin = middle + 1
        elif int(middle_line) > element:
            end = middle - 1
