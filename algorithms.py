def bubble_sort_leaderboard(user_list):
    """
    Sorts a list of (username, total_minutes) tuples by total_minutes descending.
    Uses a swapped flag so it exits early if the list is already sorted.
    Worst case O(n^2), best case O(n).
    """
    n = len(user_list)
    swapped = True

    while swapped:
        swapped = False
        for i in range(n - 1):
            if user_list[i][1] < user_list[i + 1][1]:
                user_list[i], user_list[i + 1] = user_list[i + 1], user_list[i]
                swapped = True

    return user_list


def binary_search_tracks(tracks, search_term):
    """
    Searches for a track by exact name using binary search.
    Sorts a copy of the list alphabetically first, then halves the search
    range on each step. O(log n). Case-sensitive.
    """
    sorted_tracks = sorted(tracks, key=lambda x: x.get('track_name', ''))

    low = 0
    high = len(sorted_tracks) - 1

    while low <= high:
        mid = (low + high) // 2
        mid_name = sorted_tracks[mid].get('track_name', '')

        if mid_name == search_term:
            return sorted_tracks[mid]
        elif search_term < mid_name:
            high = mid - 1
        else:
            low = mid + 1

    return None
