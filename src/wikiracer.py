import wikipediaapi
import heapq
import db
import datetime
import concurrent.futures

wiki_wiki = wikipediaapi.Wikipedia('WikiRacerBot (https://en.wikipedia.org/wiki/User:WikiRacerBot)', 'en')
DB = db.DatabaseDriver()

heuristic_cache = {}

def heuristic(current_page, end_page):
    cache_key = (current_page.title, end_page.title)
    if cache_key in heuristic_cache:
        return heuristic_cache[cache_key]
    
    current_links = set(current_page.links.keys())
    end_links = set(end_page.links.keys())
    common_links = current_links & end_links
    
    if len(current_links) == 0:
        heuristic_value = 0
    else:
        heuristic_value = (len(common_links) / len(end_links)) * 100
    
    heuristic_cache[cache_key] = heuristic_value
    
    return heuristic_value

def fetch_page(title):
    return wiki_wiki.page(title)

def a_star_search(start_page, end_page, socketio):
    minqueue = []
    settled = set()

    start = wiki_wiki.page(start_page)
    end = wiki_wiki.page(end_page)

    heapq.heappush(minqueue, (0, 0, start.title, start, [start.title], [start.canonicalurl]))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        while minqueue:
            _, cost, current_title, current_page, path, links = heapq.heappop(minqueue)

            if current_title in settled:
                continue

            settled.add(current_title)

            socketio.emit('path_update', {'path': path, 'links': links})

            if current_page.fullurl == end.title:
                socketio.emit('search_complete', {
                    'path': path,
                    'links': links,
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
                })
                DB.create_path(start.title, end.title, path, links, datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))
                heuristic_cache.clear()
                return path

            current_links = current_page.links
            futures = {}

            if len(current_links) > 1000:
                socketio.emit('size_warning', {'size': len(current_links)})

            for title in current_links.keys():
                if title not in settled:
                    futures[executor.submit(fetch_page, title)] = title

            for future in concurrent.futures.as_completed(futures):
                try:
                    next_page = future.result()
                    title = futures[future]

                    socketio.emit('new_link', {'title' : title})

                    new_path = path + [title]
                    new_links = links + [next_page.canonicalurl]

                    heuristic_calc = heuristic(next_page, end)
                    estimate = cost + 1 - heuristic_calc

                    heapq.heappush(minqueue, (estimate, cost + 1, title, next_page, new_path, new_links))

                    if heuristic_calc > 75:
                        break

                except Exception as e:
                    print(f"Error fetching {futures[future]}: {e}")
                    continue
