from unindex import patch_unindex
from dateindex import patch_dateindex
from daterangeindex import patch_daterangeindex
from extendedpathindex import patch_extendedpathindex
from languageindex import patch_languageindex
from catalog import patch_catalog

def apply():
    patch_unindex()
    patch_dateindex()
    patch_daterangeindex()
    patch_extendedpathindex()
    patch_languageindex()
    patch_catalog()
