import re


def ff(dictionary):
    for key, value in dictionary.items():
        if isinstance(value, list) and len(value) == 1:
            dictionary[key] = value[0]
        if isinstance(value, list) and len(value[0]) == 1:
            dictionary[key] = value[0][0]
    return dictionary


def find_index(regex, dict_item):
    if dict_item and isinstance(dict_item, list):
        for index, string in enumerate(dict_item):
            if re.search(regex, string):
                return index
        return -1

def find_nested_match(regex, nested_list):
    matched_lists = []
    stack = [nested_list]
    while stack:
        current_list = stack.pop(0)
        for item in current_list:
            if isinstance(item, list):
                stack.append(item)
            elif isinstance(item, str) and re.search(regex, item):
                matched_lists.append(current_list)
                break
    return matched_lists

def return_match_only(regex, dict_item):
    return re.search(regex, dict_item).group()


def remove_non_match(regex, dict_item):
    return re.sub(regex, "", dict_item)

def match_keyword(dict_of_keywords, keyword):
    return dict_of_keywords.get(keyword, None)

def title_case(strings_list, str_length):
    if strings_list and isinstance(strings_list, list):
        word = [string.strip().title() if len(string) > str_length else string for string in strings_list]
        return word[0]
    if strings_list and isinstance(strings_list, str):
        words = strings_list.split()
        capitalized_words = [word.strip().capitalize() if len(word) > str_length else word for word in words]
        return ' '.join(capitalized_words)


def sum_dollar_amounts(amounts):
    clean_amount_str = amounts[0].replace("$", "").replace(",", "")
    total = sum(int(clean_amount_str) for amount_str in amounts if amount_str)
    return total
