import pkg_resources

#Get version of a package
package_name = "pydantic" #CHANGE AS NECESSARY
version = pkg_resources.get_distribution(package_name).version
print(f"{package_name} version: {version}")