
import bitio
import huffman


def read_tree(bitreader):
	'''Read a description of a Huffman tree from the given bit reader,
	and construct and return the tree. When this function returns, the
	bit reader should be ready to read the next bit immediately
	following the tree description.

	Huffman trees are stored in the following format:
	* TreeLeaf is represented by the two bits 01, followed by 8 bits
	for the symbol at that leaf.
	* TreeLeaf that is None (the special "end of message" character)
	is represented by the two bits 00.
	* TreeBranch is represented by the single bit 1, followed by a
	description of the left subtree and then the right subtree.

	Args:
	bitreader: An instance of bitio.BitReader to read the tree from.

	Returns:
	A Huffman tree constructed according to the given description.
	'''
	#since bitreader is an instance of bitio.BitReader, we use readbit() to read first bit
	first_bit = bitreader.readbit()
	#if first bit is 1 means start from 1, it is branch
	if first_bit == 1:
		#read left sub tree until reach leaf		
		leftsub = read_tree(bitreader)
		#read right sub tree until reach leaf
		rightsub = read_tree(bitreader)
		#build the huffman tree branch
		Branch = huffman.TreeBranch(leftsub, rightsub)
		return Branch

	else:
		#there is a leaf
		second_bit = bitreader.readbit()
		#if second bit is 0 means EOF reached
		if second_bit == 0:
			#build the huffman tree leaf
			Eof = huffman.TreeLeaf(None)
			return Eof
		elif second_bit == 1:
			#if second bit is 1 means there is a character, read the bits of character
			value = bitreader.readbits(8)
			#build the huffman tree leaf and store the 8 bits
			valueleaf = huffman.TreeLeaf(value)
			return valueleaf



def decode_byte(tree, bitreader):
	"""
	Reads bits from the bit reader and traverses the tree from
	the root to a leaf. Once a leaf is reached, bits are no longer read
	and the value of that leave is returned.

	Args:
	bitreader: An instance of bitio.BitReader to read the tree from.
	tree: A Huffman tree.

	Returns:
	Next byte of the compressed bit stream.
	"""
	#the root node of tree
	node = tree
	#to decode, we should get the tree leaf value
	while isinstance(node, huffman.TreeBranch):
		#avoid the EOFError
		try:
			bit = bitreader.readbit()
		except EOFError:
			break
		#traverse the tree to reach the leaf
		if bit == 0:
			node = node.left
		elif bit == 1:
			node = node.right
		#if reach the leaf return the value of leaf
		if isinstance(node, huffman.TreeLeaf):
			return node.value
			break
	

def decompress(compressed, uncompressed):
	'''First, read a Huffman tree from the 'compressed' stream using your
	read_tree function. Then use that tree to decode the rest of the
	stream and write the resulting symbols to the 'uncompressed'
	stream.

	Args:
	compressed: A file stream from which compressed input is read.
	uncompressed: A writable file stream to which the uncompressed
	output is written.

	'''

	#let compressed be an instance of bitio.BitReader
	reading = bitio.BitReader(compressed)
	#use read_tree to get the huffman tree
	tree = read_tree(reading)
	#let uncompressed be an instance of bitio.BitWriter
	Target = bitio.BitWriter(uncompressed)

	while True:
		#get the value of leaf
		val = decode_byte(tree, reading)
		
		#if EOF just break
		if val is None:
			break

		#write the value of leaf to uncompressed file
		Target.writebits(val,8)

	Target.flush()







def write_tree(tree, bitwriter):
	'''Write the specified Huffman tree to the given bit writer.  The
	tree is written in the format described above for the read_tree
	function.

	DO NOT flush the bit writer after writing the tree.

	Args:
	tree: A Huffman tree.
	bitwriter: An instance of bitio.BitWriter to write the tree to.
	'''
	# let node be the root node of tree first
	node = tree
	#if node is branch, write 1 and go left and right children
	if isinstance(node, huffman.TreeBranch):
		bitwriter.writebit(1)
		write_tree(node.left, bitwriter)
		write_tree(node.right, bitwriter)
	#if reach the leaf
	elif isinstance(node, huffman.TreeLeaf):
		#if EOF,write EOF (00)
		if node.value is None:
			bitwriter.writebit(0)
			bitwriter.writebit(0)
		else:
			#write character bits 01 followed by 8 bits of character
			bitwriter.writebit(0)
			bitwriter.writebit(1)
			bitwriter.writebits(node.value,8)



def compress(tree, uncompressed, compressed):
	'''First write the given tree to the stream 'compressed' using the
	write_tree function. Then use the same tree to encode the data
	from the input stream 'uncompressed' and write it to 'compressed'.
	If there are any partially-written bytes remaining at the end,
	write 0 bits to form a complete byte.

	Flush the bitwriter after writing the entire compressed file.

	Args:
	tree: A Huffman tree.
	uncompressed: A file stream from which you can read the input.
	compressed: A file stream that will receive the tree description
	and the coded input data.
	'''
	##let compressed be an instance of bitio.BitWriter
	Target = bitio.BitWriter(compressed)
	#let uncompressed be an instance of bitio.BitReader
	readingfile = bitio.BitReader(uncompressed)
	#Write the Huffman tree to compressed file.
	write_tree(tree, Target)

	#to get encoding table 
	encode = huffman.make_encoding_table(tree)
	while True:
		# try EOFError
		try:
			# can read a byte ?
			reading = readingfile.readbits(8)	
		except EOFError:
			# reach EOF encode eof,then get out of loop
			Target.writebit(0)
			Target.writebit(0)
			break
		#if no EOFError, get the sequence from tree using encoding table

		value = encode[reading]
		for v in value:
			# write v as a bit
			Target.writebit(v)

	Target.flush()
