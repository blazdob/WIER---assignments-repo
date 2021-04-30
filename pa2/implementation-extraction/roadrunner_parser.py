# Tag attributes are ignored.
#
# Strings are not parially matched. If strings differ, they are generalized into most
# permissive regex (any number of any characters). This is why do_match() returns
# true on NavigableString elements.

import os.path
import copy

from bs4 import BeautifulSoup, NavigableString, Tag, Comment


ITERATOR_WRAPPER = 1
ITERATOR_SAMPLE = 2


crescenzi_wrapper1 = """
<html>
Books of:
<b>
    John Smith
</b>
<ul>
    <li>
        <i>Title:</i>
        DB Primer
    </li>
    <li>
        <i>Title:</i>
        Comp. Sys.
    </li>
</ul>
</html>"""

crescenzi_sample1 = """
<html>
Books of:
<b>
    Paul Jones
</b>
<img src="blablabla"/>
<ul>
    <li>
        <i>Title:</i>
        XML at Work
    </li>
    <li>
        <i>Title:</i>
        HTML Scripts
    </li>
    <li>
        <i>Title:</i>
        Javascript
    </li>
</ul>
</html>"""

crescenzi_wrapper2 = """
<html>Books of:<b>John Smith</b>
<ul>
    <li>
        Computer Systems
        <p>
            <b>
                1st Ed., 1995
            </b>
        </p>
    </li>
    <li>
        Database Primer
        <p>
            <b>
                1st Ed., 1998
                <i>Special!</i>
            </b>
            <b>
                2nd Ed., 2000
            </b>
        </p>
    </li>
</ul>
</html>"""

crescenzi_sample2 = """
<html>Books of:<b>John Smith</b>
<ul>
    <li>
        XML at Work
        <p>
            <b>
                1st Ed., 1999
            </b>
        </p>
    </li>
</ul>
</html>"""

iterators = set()
optionals = set()


def match_strings_and_optionals(wrapper, sample):
    # if not wrapper.contents or not sample.contents: return

    # if wrapper.contents:
    #     print(wrapper.contents)
    #     welem = wrapper.contents[0]
    # else:
    #     welem = None
    # if sample.contents:
    #     print(sample.contents)
    #     selem = sample.contents[0]
    # else:
    #     selem = None
    # while True:
    #     print("welem: {}".format(welem))
    #     print("selem: {}".format(welem))
    #     if not welem or not selem:
    #         break

    #     # match strings
    #     if isinstance(welem, NavigableString) and isinstance(selem, NavigableString):
    #         str1 = str(welem)
    #         str2 = str(selem)
    #         matchstr = match_strings(str1, str2)
    #         print("str1: {}, str2: {}, matchstr: {}".format(str1, str2, matchstr))
    #         welem.string.replace_with(matchstr)
    #         selem.string.replace_with(matchstr)
    #         welem = welem.next_sibling
    #         selem = selem.next_sibling
    #         continue

    #     if isinstance(welem, Tag) and isinstance(selem, Tag):
    #         if welem.name == selem.name:
    #             print("recursively matching")
    #             # match same tags recursively
    #             match_strings_and_optionals(welem, selem)
    #             welem = welem.next_sibling
    #             selem = selem.next_sibling
    #             continue

    #     # "greedy" string matching
    #     # optional tag in sample when string is current in wrapper and next in sample
    #     if isinstance(welem, NavigableString) and isinstance(selem.next_sibling, NavigableString):
    #         optional = copy.copy(selem)
    #         optionals.add(optional)
    #         welem.insert_before(optional)
    #         selem = selem.next_sibling
    #         continue

    #     # "greedy" string matching
    #     # optional tag in wrapper when string is current in sample and next in wrapper
    #     if isinstance(selem, NavigableString) and isinstance(welem.next_sibling, NavigableString):
    #         optionals.add(welem)
    #         welem = welem.next_sibling
    #         continue

    #     # check one step forward in both sample and wrapper
    #     if isinstance(selem.next_sibling, Tag) and selem.next_sibling.name == welem.name:
    #         # next in sample is the same tag as current wrapper tag, designate current
    #         # sample tag as optional and try to match next sample tag in next loop iteration
    #         optional = copy.copy(selem)
    #         optionals.add(optional)
    #         welem.insert_before(optional)
    #         selem = selem.next_sibling
    #         continue
    #     if isinstance(welem.next_sibling, Tag) and welem.next_sibling.name == selem.name:
    #         # next in wrapper is the same tag as current sample tag, designate current
    #         # wrapper tag as optional and try to match next wrapper tagin next loop iteration
    #         optionals.add(welem)
    #         welem = welem.next_sibling
    #         continue
        
    #     # none of current tags cross match next, designate sample's as optional
    #     optional = copy.copy(selem)
    #     optionals.add(optional)
    #     welem.insert_before(optional)
    #     welem = welem.next_sibling
    
    # while welem:
    #     optionals.add(welem)
    #     welem = welem.next_sibling
    # while selem:
    #     welem = wrapper.contents[-1]
    #     optional = copy.copy(selem)
    #     optionals.add(optional)
    #     welem.insert_after(selem)
    #     selem = selem.next_sibling

    wrapix = 0
    sampix = 0
    while True:
        if wrapix >= len(wrapper.contents) or sampix >= len(sample.contents):
            break

        welem = wrapper.contents[wrapix]
        selem = sample.contents[sampix]

        # match strings
        if isinstance(welem, NavigableString) and isinstance(selem, NavigableString):
            matchstr = match_strings(str(welem), str(selem))
            welem.string.replace_with(matchstr)
            selem.string.replace_with(matchstr)
            wrapix += 1
            sampix += 1
            continue

        if isinstance(welem, Tag) and isinstance(selem, Tag):
            if welem.name == selem.name:
                # match same tags recursively
                match_strings_and_optionals(welem, selem)
                wrapix += 1
                sampix += 1
                continue

        # "greedy" string matching
        # optional tag in sample when string is current in wrapper and next in sample
        if isinstance(welem, NavigableString) and isinstance(selem.next_sibling, NavigableString):
            optional = copy.copy(selem)
            wrapper.contents.insert(wrapix, optional)
            optionals.add(optional)
            wrapix += 1
            sampix += 1
            continue

        # "greedy" string matching
        # optional tag in wrapper when string is current in sample and next in wrapper
        if isinstance(selem, NavigableString) and isinstance(welem.next_sibling, NavigableString):
            optionals.add(welem)
            wrapix += 1
            continue

        # check one step forward in both sample and wrapper
        if isinstance(selem.next_sibling, Tag) and selem.next_sibling.name == welem.name:
            # next in sample is the same tag as current wrapper tag, designate current
            # sample tag as optional and try to match next sample tag in next loop iteration
            optional = copy.copy(selem)
            wrapper.contents.insert(wrapix, optional)
            optionals.add(optional)
            wrapix += 1
            sampix += 1
            continue
        if isinstance(welem.next_sibling, Tag) and welem.next_sibling.name == selem.name:
            # next in wrapper is the same tag as current sample tag, designate current
            # wrapper tag as optional and try to match next wrapper tagin next loop iteration
            optionals.add(welem)
            wrapix += 1
            continue
        
        # none of current tags cross match next, designate sample's as optional
        optional = copy.copy(selem)
        wrapper.contents.insert(wrapix, optional)
        optionals.add(optional)
        wrapix += 1
        sampix += 1
    
    while wrapix < len(wrapper.contents):
        optionals.add(wrapper.contents[wrapix])
        wrapix += 1
    while sampix < len(sample.contents):
        optional = copy.copy(selem)
        wrapper.contents.insert(wrapix, optional)
        optionals.add(optional)
        wrapix += 1
        sampix += 1


def generate_regex(wrapper):
    if isinstance(wrapper, BeautifulSoup):
        generate_regex(wrapper.html)
    if isinstance(wrapper, NavigableString):
        if wrapper in optionals:
            wrapper.string.replace_with("({})?".format(str(wrapper.string)))
    if isinstance(wrapper, Tag):
        childix = 0
        while childix < len(wrapper.contents):
            generate_regex(wrapper.contents[childix])
            if wrapper.contents[childix] in optionals and isinstance(wrapper.contents[childix], Tag):
                wrapper.contents.insert(childix, NavigableString("("))
                wrapper.contents.insert(childix + 2, NavigableString(")?"))
                childix += 3
            else:
                childix += 1


def roadrunner_parser():
    pass


def match(wrapper, sample):
    #print("match():{}\t\t{}".format(wrapper, sample))

    wrapix = 0
    sampix = 0
    while True:
        print("match(): while: wrapix = {}, sampix = {}".format(wrapix, sampix))
        wchildren = wrapper.contents
        schildren = sample.contents
        if wrapix >= len(wchildren) or sampix >= len(schildren):
            break
        welem = wchildren[wrapix]
        selem = schildren[sampix]
        print("match(): while: {}\t\t{}".format(welem, selem))

        # match strings
        if isinstance(welem, NavigableString) and isinstance(selem, NavigableString):
            str1 = str(welem)
            str2 = str(selem)
            matchstr = match_strings(str1, str2)
            welem.replace_with(NavigableString(matchstr))
            selem.replace_with(NavigableString(matchstr))
            wrapix = wrapix + 1
            sampix = sampix + 1
            continue

        # match same tags recursively
        both_tags = isinstance(welem, Tag) and isinstance(selem, Tag)
        if both_tags:
            if welem.name == selem.name:
                match(welem, selem)
                wrapix = wrapix + 1
                sampix = sampix + 1
                continue

        # handle iterators
        if isinstance(welem, Tag) and isinstance(selem, NavigableString) or \
            isinstance(welem, NavigableString) and isinstance(selem, Tag) or \
            isinstance(welem, Tag) and isinstance(selem, Tag):
            iterator = check_iterator(wchildren, schildren, wrapix, sampix)
            if iterator == ITERATOR_WRAPPER:
                welem.extract()
                iterators.add(wchildren[wrapix - 1])
                continue
            elif iterator == ITERATOR_SAMPLE:
                selem.extract()
                iterators.add(wchildren[wrapix - 1])
                continue

        # handle optionals
        wrapdist = elem_distance(selem, wchildren[wrapix + 1:])
        sampdist = elem_distance(welem, schildren[sampix + 1:])
        print("match(): distances: {}, {}".format(wrapdist, sampdist))
        if wrapdist == 0 and sampdist == 0: # keep the same in wrapper
            #welem.insert_before(selem)
            wrapper.insert(wrapix, selem)
            optionals.add(selem)
            wrapix += 1
            sampix += 1
            continue
        if wrapdist == 0:
            #welem.insert_before(selem)
            wrapper.insert(wrapix, selem)
            optionals.add(selem)
            wrapix += 1
            sampix += 1
            continue
        if sampdist == 0:
            optionals.add(welem)
            wrapix += 1
            continue
        if sampdist >= wrapdist: # also if distance is the same
            wrapix += 1
            optionals.add(welem)
            continue
        if wrapdist > sampdist:
            #welem.insert_before(selem)
            wrapper.insert(wrapix, selem)
            optionals.add(selem)
            wrapix += 1
            sampix += 1
            continue
    
    if wrapix < len(wchildren):
        for child in wchildren[wrapix:]:
            optionals.add(child)
    elif sampix < len(schildren):
        for child in schildren[sampix:]:
            optionals.add(child)


def clean_soup(soup):
    if isinstance(soup, BeautifulSoup):
        clean_soup(soup.html)
    elif isinstance(soup, NavigableString):
        if str(soup).isspace():
            soup.extract()
        else:
            newstr = str(soup.string).strip()
            soup.string.replace_with(newstr)
    elif isinstance(soup, Comment):
        soup.extract()
    else:
        ix = 0
        while ix < len(soup.contents):
            length = len(soup.contents)
            clean_soup(soup.contents[ix])
            if length == len(soup.contents):
                ix = ix + 1


# Finding distance of string elements is stupid because we don't do any more
# advanced string matching. Also, there are two possible strategies: do
# we try to match string or not? How can we know if this approach is good?
def elem_distance(elem, children):
    distance = 1
    for child in children:
        if isinstance(child, NavigableString) and isinstance(elem, NavigableString):
            return distance
        if isinstance(child, Tag) and isinstance(elem, Tag):
            if elem.name == child.name:
                return distance
        distance = distance + 1
    return 0 # we didn't find matching element


def check_iterator(wchildren, schildren, wrapix, sampix):
    if wrapix < 0 or sampix < 0:
        return False

    if not do_match(wchildren[wrapix - 1], schildren[sampix - 1]):
        return False
    
    if do_match(wchildren[wrapix - 1], wchildren[wrapix]):
        return ITERATOR_WRAPPER
    
    if do_match(schildren[sampix - 1], schildren[sampix]):
        return ITERATOR_SAMPLE

    return False


def do_match(soup1, soup2):
    # compare HTML if we get entire document
    if isinstance(soup1, BeautifulSoup) and isinstance(soup2, BeautifulSoup):
        return do_match(soup1.html, soup2.html)
    if isinstance(soup1, BeautifulSoup): return False
    if isinstance(soup2, BeautifulSoup): return False

    # both have to be tags to match; tag attributes are ignored; tags with
    # different number of children do not match (assuming comments were removed
    # from soups)
    if isinstance(soup1, Tag) and isinstance(soup2, Tag):
        if soup1.name != soup2.name:
            return False
        if len(soup1.contents) != len(soup2.contents):
            return False
        for s1elem, s2elem in zip(soup1.contents, soup2.contents):
            if not do_match(s1elem, s2elem):
                return False
        return True
    if isinstance(soup1, Tag): return False
    if isinstance(soup2, Tag): return False

    if isinstance(soup1, NavigableString) and isinstance(soup2, NavigableString):
        return True


def match_strings(s1, s2):
    if s1 == s2:
        return s1
    else:
        return ".*"


def main():
    pg_base = os.path.join("..", "input-extraction", "overstock.com")
    pg1_file = os.path.join(pg_base, "jewelry01.html")
    pg2_file = os.path.join(pg_base, "jewelry02.html")
 
    with open(pg1_file, "r") as f1:
        with open(pg2_file, "r") as f2:
            html_wrapper = f1.read()
            html_sample = f2.read()
            #wrapper_soup = BeautifulSoup(html_wrapper, "html.parser")
            #sample_soup = BeautifulSoup(html_sample, "html.parser")
            wrapper_soup = BeautifulSoup(crescenzi_wrapper1, "html.parser")
            sample_soup = BeautifulSoup(crescenzi_sample1, "html.parser")
            #wrapper_soup = BeautifulSoup(crescenzi_sample1, "html.parser")
            #sample_soup = BeautifulSoup(crescenzi_wrapper1, "html.parser")
            clean_soup(wrapper_soup)
            clean_soup(sample_soup)
            #print(wrapper_soup)
            #print(sample_soup)
            #print("##################################################################")
            match_strings_and_optionals(wrapper_soup.html, sample_soup.html)
            #print(wrapper_soup)
            #print(sample_soup)
            #print("##################################################################")
            generate_regex(wrapper_soup)
            print(wrapper_soup)
            #print(optionals)


if __name__ == "__main__":
    main()