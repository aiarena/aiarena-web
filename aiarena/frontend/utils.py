
def restrict_page_range(num_pages, page_number):
    if num_pages <= 11 or page_number <= 6:  # case 1 and 2
        return [x for x in range(1, min(num_pages + 1, 12))]
    elif page_number > num_pages - 6:  # case 4
        return [x for x in range(num_pages - 10, num_pages + 1)]
    else:  # case 3
        return [x for x in range(page_number - 5, page_number + 6)]