from treelib import Node, Tree
import sys

# Set the encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

tree = Tree()
tree.create_node("Harry", "harry")  # root node
tree.create_node("Jane", "jane", parent="harry")
tree.create_node("Bill", "bill", parent="harry")
tree.create_node("Test", "test", parent="harry")
tree.create_node("Test2", "test2", parent="harry")
tree.create_node("Diane", "diane", parent="jane")
tree.create_node("Mary", "mary", parent="diane")
tree.create_node("Mark", "mark", parent="jane")

# Encode the labels to UTF-8 before showing the tree
encoded_tree = tree.to_json(with_data=True).encode('utf-8')
decoded_tree = encoded_tree.decode('utf-8')
tree.show()
