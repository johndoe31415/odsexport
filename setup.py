import setuptools

with open("README.md") as f:
	long_description = f.read()

setuptools.setup(
	name = "odsexport",
	packages = setuptools.find_packages(),
	version = "0.0.4",
	license = "gpl-3.0",
	description = "Python-native ODS writer library",
	long_description = long_description,
	long_description_content_type = "text/markdown",
	author = "Johannes Bauer",
	author_email = "joe@johannes-bauer.com",
	url = "https://github.com/johndoe31415/odsexport",
	download_url = "https://github.com/johndoe31415/odsexport/archive/0.0.4.tar.gz",
	keywords = [ "python", "ods", "excel", "spreadsheet" ],
	install_requires = [ ],
	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3 :: Only",
		"Programming Language :: Python :: 3.12",
	],
)
