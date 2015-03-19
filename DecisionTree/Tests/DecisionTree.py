import sys
import unittest
from fractions import Fraction
from math import log

class Node:
	def __init__(self, vote_index, examples=None, attributes=None, parent_examples=None):
		self.vote_index = vote_index
		self.children = {} #Children are key'd by values of attribute

		#Used for Leaf nodes
		self.value = None
		self.prob = 0
		
		#Used for pruning
		self.parent = None
		self.examples = examples
		self.attributes = attributes
		self.parent_examples = parent_examples

	def is_leaf(self):
		return len(self.children) == 0

	def is_prunable(self):
		"""Return True if all children are leaves, otherwise False."""
		for child in self.children.values():
			if not child.is_leaf():
				return False
		return True

	def decide(self, votes):
		child_key = votes[self.vote_index-1] #vote_index is shifted by 1 b/c the training data includes a class label at the beginning
		return self.children[child_key]	

class DecisionTree:

	def __init__(self, training_filename, pruning=False):
		examples = []
		with open(training_filename) as training_file:
			for entry in training_file:
				values = entry.replace("\n", "").split(",")
				examples.append(values)

		self.num_votes = len(examples[0]) - 1
		self.root = self._decision_tree_learning(examples, range(1,len(examples[0])), [])
		
		if pruning:
			self._prune()
	
	def _decision_tree_learning(self, examples, attributes, parent_examples):
		if len(examples) == 0:
			leaf = Node(None, examples=examples, attributes=attributes, parent_examples=parent_examples)
			leaf.value = self._plurality_value(parent_examples)
			leaf.prob = float(len([e for e in parent_examples if e[0] == leaf.value])) / float(len(parent_examples))
			return leaf
		elif self._all_same_party(examples): 
			leaf = Node(None, examples=examples, attributes=attributes, parent_examples=parent_examples)
			leaf.value = examples[0][0]
			leaf.prob = 1.0
			return leaf
		elif len(attributes) == 0:
			leaf = Node(None, examples=examples, attributes=attributes, parent_examples=parent_examples)
			leaf.value = self._plurality_value(examples)
			leaf.prob = float(len([e for e in examples if e[0] == leaf.value])) / float(len(examples)) 
			return leaf
		else:
			attribute = max(attributes, key=lambda x: self._importance(x, examples))
			node = Node(attribute, examples=examples, attributes=attributes, parent_examples=parent_examples)

			new_attributes = attributes[:]
			new_attributes.remove(attribute)

			for value in ["n", "y"]:
				matching_examples = [example for example in examples if example[attribute] == value]
				node.children[value] = self._decision_tree_learning(matching_examples, new_attributes, examples)
				node.children[value].parent = node

			return node

	def _plurality_value(self, examples):
		"""Return the most popular first entry (party) of each example."""
		party_count = {"republican":0, "democrat":0}
		for example in examples:
			party_count[example[0]] += 1	
		
		if party_count["republican"] >= party_count["democrat"]:
			return "republican"
		else:
			return "democrat"
		
	def _all_same_party(self, examples):
		"""Return True if the first entry (the party) in each example is the same."""
		assert len(examples) > 0
		party = examples[0][0]
		for example in examples:
			if example[0] != party:
				return False
		return True
	
	def _importance(self, attribute, examples):
		"""Return the information gain from the attribute test on the given examples."""
		count = {"republican":0, "democrat":0}
		for example in 	examples:
			count[example[0]] += 1	
		B = self._B(count["republican"], count["democrat"])
	
		return B - self._remainder(attribute, examples)
		
	def _B(self, p, n):
		"""Return the entropy of a the Boolean variable specified by attribute."""
		if p == 0 or n == 0:
			return 0

		q = float(p) / float(p+n)
		return -(q*log(q,2) + (1-q)*log(1-q,2))

	def _remainder(self, attribute, examples):
		remainder = 0

		count = {"republican":0, "democrat":0}
		for example in 	examples:
			count[example[0]] += 1	

		for value in ["n", "y"]:
			count_k = {"republican":0, "democrat":0}
			for example in 	examples:
				if example[attribute] == value:
					count_k[example[0]] += 1	
			
			B = self._B(count_k["republican"], count_k["democrat"])
			remainder += B * float(count_k["republican"] + count_k["democrat"]) / float(count["republican"] + count["democrat"])

		return remainder

	def classify(self, votes):
		"""Return (party, prob) given the votes and the training set.
		@param votes: a list of votes: "y", "n", "?" """
		assert self.num_votes == len(votes)
		assert set(["y", "n"]).issuperset(set(votes))

		curr_node = self.root

		while not curr_node.is_leaf():
			curr_node = curr_node.decide(votes)	

		return (curr_node.value, curr_node.prob)	

	def _print(self):
		nodes = [self.root]
		while len(nodes) > 0:
			node, nodes = nodes[0], nodes[1:]
			if node.is_leaf():
				print "Leaf:",node.value, node.prob
			else:
				print "Split:",node.vote_index, "(",node.children['y'].vote_index,node.children['n'].vote_index,')'

			for child in node.children.values():
				nodes.append(child)	

	def _prune(self):
		
		prunable_nodes = [] #Nodes that have only leaf children

		#Explore the current tree to find all leaf nodes	
		nodes = [self.root]
		while len(nodes) > 0:
			node, nodes = nodes[0], nodes[1:]
			for child in node.children.values():
				nodes.append(child)

			if node.is_prunable():
				prunable_nodes.append(node)
	
		#Try to prune all prunable nodes
		while len(prunable_nodes) > 0:
			node, prunable_nodes = prunable_nodes[0], prunable_nodes[1:]	
	
			#If nodes aren't significant, replace the node with a leaf	
			if not self._significant(node):
				leaf = Node(None, examples=node.examples, attributes=node.attributes, parent_examples=node.parent_examples)
				leaf.value = self._plurality_value(node.examples)
				leaf.prob = float(len([e for e in node.examples if e[0] == leaf.value])) / float(len(node.examples)) 
				leaf.parent = node.parent	

				if node.parent is None:
					continue
				else:
					#Replace node with leaf in the parent's list of children
					node_key = None
					for key, child in node.parent.children.iteritems():
						if child == node:
							node_key = key
							break
					node.parent.children[key] = leaf

					if node.parent.is_prunable():
						prunable_nodes.append(node.parent)	
				
	def _significant(self, node):
		"""Return True if the node is significant at the 5% level according to the chi-squared distrubtion with 1 df."""
		x_square_cutoff = 3.841 #1df @ 5% level
		x_square_node = float("inf") 

		return x_square_node > x_square_cutoff
			

class DTTest(unittest.TestCase):

	def setUp(self):
		self.dt = DecisionTree("test/simple.data")

	def test_plurality_value(self):
		examples = [["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"]]
		self.assertEqual(self.dt._plurality_value(examples), "republican")
	
		examples = [["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["democrat", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["democrat", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"]]
		self.assertEqual(self.dt._plurality_value(examples), "republican")
		
		examples = [["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"]]
		self.assertEqual(self.dt._plurality_value(examples), "republican")

		examples = [["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["democrat", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["democrat", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["democrat", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"]]
		self.assertEqual(self.dt._plurality_value(examples), "democrat")

		examples = [["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["democrat", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["democrat", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"]]
		self.assertEqual(self.dt._plurality_value(examples), "republican")

	def test_all_same_party(self):
		examples = [["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"]]
		self.assertTrue(self.dt._all_same_party(examples))
	
		examples = [["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["democrat", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["democrat", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"]]
		self.assertFalse(self.dt._all_same_party(examples))
		
		examples = [["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"]]
		self.assertTrue(self.dt._all_same_party(examples))

		examples = [["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["democrat", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["democrat", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["democrat", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"]]
		self.assertFalse(self.dt._all_same_party(examples))

		examples = [["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["democrat", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["democrat", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"],
			    ["republican", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"]]
		self.assertFalse(self.dt._all_same_party(examples))

	def test_B(self):
		self.assertEqual(self.dt._B(0,0), 0)
		self.assertEqual(self.dt._B(0,5), 0)
		self.assertEqual(self.dt._B(10,0), 0)

		self.assertEqual(self.dt._B(1,1), 1)
		self.assertAlmostEqual(self.dt._B(99,1), 0.08, places=2)

	def test_remainder(self):
		pass
	
	def test_importance(self):	
		pass

if __name__ == "__main__":

	if len(sys.argv) <= 1:
		unittest.main()
		sys.exit(0)
		
	training_filename, test_filename = sys.argv[1], sys.argv[2]
	enable_pruning = (len(sys.argv) == 4) and (sys.argv[3] == "enabled")

	classifier = DecisionTree(training_filename, pruning=enable_pruning)
	with open(test_filename) as test_file:
		for test in test_file:
			party, prob = classifier.classify(test.replace("\n", "").split(","))
			print "{0},{1}".format(party, float(prob))
	#classifier._print()
