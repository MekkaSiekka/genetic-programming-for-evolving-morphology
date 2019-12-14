#include <iostream>
#include <vector>
#include <algorithm>
#include <list>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <chrono>
#include <cstdlib>
#include <set>
#include <string>
#include <bits/stdc++.h> 
#include <valarray>

using namespace std;

struct Node{
	Node * left;
	Node * right;
	int val;
};

void build_helper(int level, Node * n){
	cout<<level<<endl;
	n->left = new Node;
	n->left->val = level;
	n->right-> val = level;
	++level;
	build_helper(level, n->left);
	build_helper(level, n->right);
}

Node * build(int i){
	cout<<i<<endl;
	if (i==3) return NULL;
	else {
		Node * nd = new Node;
		i = i+1;
		nd->left = build(i);
		nd->right = build(i);
		nd ->val = i;
		return nd;
	} 
}


int main(){
	Node * root = build(0);
}