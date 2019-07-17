'''
test/str_holder test file
'''

import pytest

from str_holder import StrHolder, DuplicationError


TEST_STR_HOLDER_HOLDER = StrHolder()


@pytest.mark.parametrize('string', ['a', 'b', 'c'])
def test_str_holder(string):
    '''If inputs are different, do nothing.'''
    TEST_STR_HOLDER_HOLDER.add(string)


TEST_STR_HOLDER_SAME_HOLDER = StrHolder()


@pytest.mark.parametrize('string', ['a', 'b', 'c', 'A'])
def test_str_holder_same(string):
    '''If inputs are not different, raise DuplicationError'''
    if string.islower():
        TEST_STR_HOLDER_SAME_HOLDER.add(string)
    else:
        with pytest.raises(DuplicationError):
            TEST_STR_HOLDER_SAME_HOLDER.add(string.lower())
