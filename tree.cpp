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
#include "system.hpp"
using namespace std;

int LEN = 32;
long EVAL_LIM = 20000;
int POP_SIZE = 96;
double THRESH = 0.4;


vector<valarray<double>> dir_bank;
vector<vector<valarray<double>>> shape_bank;
vector<vector<int>> property_bank;

double get_size(vector<valarray<double>> shape){
	auto minv = shape[0];
	auto maxv = shape[0];
	for (auto s : shape){
		for (int i =0; i <3; i++){
			minv[i] = min(s[i],minv[i]);
			maxv[i] = max(s[i],maxv[i]);
		}
	}
	maxv -=minv;
	return abs(maxv.max());
}

//helper function to print node
double arr_to_hash(valarray<double> l){
	double h =10000*l[0]+100*l[1]+l[2]; 
	return h;
}


class Node{
public:
	Node (){}
	Node(string type_in){
		type = type_in;
		if (type_in=="op"){
			rand_op();
		}
		else rand_shape();
	}

	Node(const Node & n2){
		level = n2.level;
		type = n2.type;
		shape = n2.shape;
		property = n2.property;
		dir = n2.dir;
	}
	vector<valarray<double>> get_shape(){
		return shape;
	}
	vector<int> get_property(){
		return property;
	}
	void set_shape(vector<valarray<double>> s){
		shape = s;
	}
	void set_property(vector<int> p){
		property = p;
	}
	valarray<double> get_dir(){
		return dir;
	}

	void prt(){
		cout<<"----------------"<<endl;
		cout<<"Level  "<<level<<endl;;
		cout<<"Type  " <<type<<endl;
		if (type == "op"){
			cout << "dir "<<arr_to_hash(dir)<<endl;
		}
		else {
			double r = 0;
			for (auto & s : shape){
				r+= arr_to_hash(s);
			}
			cout<< "hash "<< r <<endl;
		}
	}

	void mutate(){
		if (type == "op"){
			dir = dir_bank[rand()%dir_bank.size()];
			return;
		}
		//swap head and tail position and property 
		//change 5% cube's property
		//change shape of a block
		int i = rand()%4;
		if (i==0){
			reverse(begin(shape),end(shape));	
			return;
		}
		if (i==1){
			reverse(begin(property),end(property));
			return ;
		}
		if (i==2){
			shape = shape_bank[rand()%shape_bank.size()];
		}
		else{
			property = property_bank[rand()%property_bank.size()];
		}
		
	}

	int level;
	string type;
	vector<valarray<double>> shape;
	vector<int> property;
	valarray<double> dir;
private:
	void rand_op(){
		int dir_idx = rand()%dir_bank.size();
		dir = dir_bank[dir_idx];
		type = "op";
	}
	void rand_shape(){
		int shape_idx = rand()%shape_bank.size();
		shape = shape_bank[shape_idx];
		//prt_arr(shape[0]);
		int property_idx = rand()%property_bank.size();
		property = property_bank[property_idx];
		int rd = rand()%2;
		if (rd == 0){
			//swap(head,tail);
			std::reverse(std::begin(shape), std::end(shape));
			std::reverse(std::begin(property),std::end(property));
		}
		type = "s";
	}
};



class EXPR{
public:
	EXPR(){}
	void init(){
		v = rand_expr();
	}
	EXPR(const EXPR& e2){
		//fitness = e2.fitness;
		//root = copy_tree(e2.root);
		v= e2.v;
		fitness = e2.fitness;
	}
	//returns a nice robot with property
	Node assemble(){
		return assem_help(1);
	}

	//copy a child the same as this, and crossover with p2. 
	EXPR crossover(EXPR p2){
		EXPR c;
		c.v = v;
		c.fitness = fitness;
		int rd_level = rand()%LEN;
		while (rd_level == 0){
			rd_level = rand()%LEN;
		}
		//cout<<"--------Rand Level"<<rd_level<<"------------"<<endl;
		c.mod_subtree(p2,rd_level);
		return c;
	}

	void prt_EXPR(){
		for (int i = 0; i < v.size(); i++){
			cout<<i<<endl;
			v[i].prt();
		}
	}

	void mutate(){
		int rd = rand()%LEN;
		v[rd].mutate();
	}

	void set_fitness(double f){
		fitness =f ;
	}

	double get_fitness(){
		return fitness;
	}
	map<int,Node> v;
	double fitness;

private:
	
	map<int,Node> rand_expr(){
		map<int,Node> new_v;
		for (int i = 0; i < LEN; ++i){
			new_v[i] = Node("s");
			new_v[i].level = i;
		}
		for (int i = 0; i < LEN/2; ++i){
			new_v[i] = Node("op");
			new_v[i].level = i;
		}
		return new_v;
	}

	Node assem_help(int i){
		if (2*i>=LEN){
			if (v[i].type !="s"){
				cout<<"why"<<endl;
				v[i].prt();
				cout<<"i"<<i<<endl;
				cout<<"prev"<<endl;
				v[i/2].prt();
			}
			assert(v[i].type=="s");
			return v[i];
		} 
		else{
			Node lhs = assem_help(2*i);
			Node rhs = assem_help(2*i+1);
			vector<valarray<double>> l_shape = lhs.get_shape();
			vector<valarray<double>> r_shape = rhs.get_shape();
			valarray<double> core = l_shape.front();
			valarray<double> cur = r_shape.back();
			valarray<double> dif = core - cur;
			vector<int> l_property = lhs.get_property();
			vector<int> r_property = rhs.get_property();
			valarray<double> dir = v[i].get_dir();
			for (auto & p : r_shape){
				p+= dif;
			}
			
			while (check_collision(l_shape, r_shape)){
				for (auto & p : r_shape){
					p += dir;
				}
			}
			for (auto & p : r_shape){
				l_shape.push_back(p);
			}
			for (auto & prop :  r_property){
				l_property.push_back(prop);
			}
			Node ret = lhs;
			ret.set_shape(l_shape);
			ret.set_property(l_property);
			ret.type ="s";
			return ret; 
		}
	}


	void  mod_subtree(EXPR & expr2, int idx){
		if (idx>=LEN) return;
		//cout<<"~~~~~~VS"<<endl;
		//v[idx].prt();
		//expr2.v[idx].prt();
		//cout<<"!!!!!!!!"<<endl;
		v[idx] = expr2.v[idx];
		mod_subtree(expr2,idx*2);
		mod_subtree(expr2,idx*2+1);
	}


};


void sanity(vector<valarray<double>>locs){
	unordered_set<double> mp;
	for (auto l : locs){
		double h =10000*l[0]+100*l[1]+l[2]; 
		if (mp.find(h)!=mp.end()) cout<<"WRONG"<<endl;
		mp.insert(h);
	}
}

bool CompMore(EXPR  & g1, EXPR & g2)
{
    return g1.get_fitness()>g2.get_fitness();
} 


// void step_RD(map<double, EXPR>  &  population){
	
// 	uint size = population.size();
// 	#pragma omp parallel for
// 	for (uint j = 0; j<size; j++){
// 		EXPR e;
// 		e.init();
// 		Node n = e.assemble();
// 		System s(n.get_shape(),n.get_property());
// 		double dist = s.sim();
// 		e.set_fitness(dist/get_size(n.get_shape()));
// 		#pragma omp critical(dataupdate)
// 		{
// 			if (e.get_fitness()>population.begin()->first) {
// 				population.erase(population.begin()->first);
// 				population[e.get_fitness()]=e;
// 			}
// 		}	
// 	}

// }



void step_EA(vector<EXPR> &  population){
	uint size = POP_SIZE;
	#pragma omp parallel for
	for (uint j = 0; j<size/2; j++){
		//cout<<"1itr  "<<itr1->first<< "2itr  "<<itr2->first<<endl;
		int rd1 = rand()%population.size();
		int rd2 = rand()%population.size();
		EXPR p1,p2;
		#pragma omp critical
		{
			p1 = population[rd1]; 
			p2 = population[rd2]; 
		}
		
		//#pragma omp critical
		//{cout<<"pareNt finess"<<p1.get_fitness()<<endl;}
		EXPR c1 = p1.crossover(p2);
		EXPR c2 = p2.crossover(p1);
		//cout<<"before mutate"<<endl;
		c1.mutate();
		c2.mutate();
		Node n1 = c1.assemble();
		Node n2 = c2.assemble();
		//cout<<"after assemble"<<endl;
		System s1(n1.get_shape(),n1.get_property());
		System s2(n2.get_shape(),n2.get_property());
		double dist1 = s1.sim();
		double dist2 = s2.sim();
		c1.set_fitness(dist1/get_size(n1.get_shape()));
		c2.set_fitness(dist2/get_size(n2.get_shape()));
		//cout<<"bef replacing"<<endl;
		if (c1.get_fitness()>p1.get_fitness()){
			#pragma omp critical(dataupdate)
			population[rd1] = c1;
		}
		if (c2.get_fitness()>p2.get_fitness()){
			#pragma omp critical(dataupdate)
			population[rd2] = c2;
		}
	}
	sort(population.begin(),population.end(),CompMore);
	// for (auto & p:population){
	// 	cout<<p.get_fitness()<<endl;
	// }
}

// void step_HC(map<double, EXPR> &  population){
// 	uint size = population.size();
// 	vector<double> keys;
// 	map<double, EXPR>::iterator itr;
// 	for (itr = population.begin(); itr != population.end(); itr++ )
// 	{
// 	    keys.push_back(itr->first);
// 	}
//  	#pragma omp parallel for
// 	for (int i = 0; i<keys.size(); i++){
// 		EXPR e = EXPR(population[keys[i]]);
// 		e.mutate();
// 		Node n = e.assemble();
// 		System s(n.get_shape(),n.get_property());
// 		double dist = s.sim();
// 		//cout<<"shape size"<<get_size(n.get_shape())<<endl;
// 		e.set_fitness(dist/get_size(n.get_shape()));
// 	 	#pragma omp critical(dataupdate)
// 		population[e.get_fitness()] = e;
// 	}
// 	cout<<"before"<<population.size()<<endl;
// 	//sort(population.begin(),population.end(),CompMore);

// 	int cut = population.size()-POP_SIZE;
// 	for (uint i=0 ; i< cut;i ++){
// 		population.erase(population.begin());
// 	}
// 	cout<<"after"<<population.size()<<endl;
// }

// void step_RD(map<double, EXPR> &  population){

// }


void start(){

	LOC_SIZE = locs.size();

	vector<EXPR> population;
	map<int,double> convergence;
	map<int,double> fitness;
	map<int,double> diversity;
	map<int,vector<double>> dot;
 
 	cout<<"Building Pop"<<endl;
 	#pragma omp parallel for
	for (int p = 0; p < POP_SIZE; p ++){
		EXPR e;
		e.init();
		Node n = e.assemble();
		sanity(n.get_shape());
		System s(n.get_shape(),n.get_property());
		double dist = s.sim();
		e.set_fitness(dist/get_size(n.get_shape()));
		#pragma omp critical(dataupdate)
		population.push_back(e);
	}
	
	uint r = 0;
	cout<<"finished building pop, size"<<population.size()<<endl;
	while (1){
		r ++;
		EVAL += POP_SIZE;
		if (EVAL > EVAL_LIM){
			break;
		}
		//if (TYPE == "HC") step_HC(population);
		if (TYPE == "EA") step_EA(population);
		//if (TYPE == "RD") step_RD(population);

		cout<<EVAL<< "|"<<population.front().get_fitness()<<endl;
		cout<<population.size()<<endl;
		

		double total_dist = 0;
		vector<double> dots;
		int c = 0;
		for(auto & p : population){
			convergence.insert({EVAL,0});
			if (p.get_fitness() > THRESH){
				convergence.insert(pair<int,double>(EVAL,1-(c+1)/(double)population.size()));
				break;
			} 
			//keep track of dot 
			dots.push_back(p.get_fitness());
			for (auto & p2 : population){
				//total_dist += abs(itr1-	>get_fitness() - itr2->get_fitness());
				total_dist += 0.1;
			}
			c++;
		}
		fitness.insert({EVAL,population.front().get_fitness()});
		
		// //build both dot plot and diversity plot
		// for (uint i = 0; i < POP_SIZE; ++i)
		// {
		// 	dots.push_back(population[i].get_fitness()/SIM_TIME);
		// 	for (uint j = 0; j < population.size(); ++j)
		// 	{
		// 		//cout<<population[i].distance(population[j])<<endl;
		// 		total_dist += population[i].distance(population[j]);
		// 	}
		// }


		//total_dist = total_dist/population.size()/population.size();
		diversity.insert(pair<int,double>(r,total_dist));
		dot.insert({r,dots});

	}
	//-----------Output the model with a longer simulation time ---------------
	EXPR e = population.front();
	Node n = e.assemble();

	System s(n.get_shape(),n.get_property());
	double tddd = s.sim_long();
	for (auto s: n.get_shape()){
		prt_arr(s);
	}
	for (auto p : n.get_property()){
		cout<<p<<endl;
	}



	//-----------Output plots etc. ----------------------------------------------
	cout<<"outputing"<<endl;
	s.output_model();
	s.output_simul();

	cout<<"convergence"<<endl;
	for (auto  k = convergence.begin(); k!=convergence.end();k++){
		cout<<k->first<<" "<<k->second<<endl;
	}
	cout<<"fitness"<<endl;
	for (auto  k = fitness.begin(); k!=fitness.end();k++){
		cout<<k->first<<" "<<k->second<<endl;
	}
	cout<<"diversity"<<endl;
	for (auto  k = diversity.begin(); k!=diversity.end();k++){
		cout<<k->first<<" "<<k->second<<endl;
	}
	cout<<"dot"<<endl;
	for (auto  k = dot.begin(); k!=dot.end();k++){
		cout<<k->first<<" "<<k->second[0]<<endl;
	}

	string file_name = TYPE+to_string(rand())+".txt";
	ofstream myfile;
	myfile.open (file_name);
	myfile << convergence.size()<<endl;
	for (auto  k = convergence.begin(); k!=convergence.end();k++){
		myfile <<  k->first << " "<< k->second<<std::endl;
	}
	myfile << fitness.size()<<endl;
	for (auto  k = fitness.begin(); k!=fitness.end();k++){
		myfile<< k->first << " " << k->second<<endl;
	}
	myfile << diversity.size()<<endl;
	for (auto  k = diversity.begin(); k!=diversity.end();k++){
		myfile<<k->first<<" "<<k->second<<endl;
	} 
	myfile << dot.size()<<endl; //number of generation
	for (auto  k = dot.begin(); k!=dot.end();k++){
		myfile<<k->first<<" "<<endl;
		myfile<<k->second.size()<<endl;
		for (auto & d:k->second ){
			myfile<< d <<endl;
		}
	}
	myfile.close();
}


void test(){
	EXPR e;
	e.init();
	e.prt_EXPR();
	e.mutate();
	cout<<endl;
	e.prt_EXPR();
	Node n = e.assemble();
	cout<<"assemble"<<endl;
	
	auto v = n.get_shape();
	for (auto l : v){
		prt_arr(l);
	}
	for (auto p : n.get_property()){
		cout<<p<<endl;
	}
}

void init_shapes(){
	shape_bank.push_back({{0,1,0},{0,2,0},{0,3,0}});
	shape_bank.push_back({{0,0,0},{1,0,0},{2,0,0}});
	shape_bank.push_back({{0,0,0},{0,0,1},{0,0,2}});

	
	shape_bank.push_back({{1,0,0},{0,0,0},{0,-1,0}});
	shape_bank.push_back({{-1,0,0},{0,0,0},{0,-1,0}});
	shape_bank.push_back({{0,0,0},{-1,0,0},{0,-1,0}});
	shape_bank.push_back({{0,0,0},{1,0,0},{0,-1,0}});
	
	
	property_bank.push_back({1,2,3});
	property_bank.push_back({1,3,2});
	property_bank.push_back({0,2,3});
	property_bank.push_back({0,0,0});
	property_bank.push_back({1,1,1});
	property_bank.push_back({2,2,2});
	property_bank.push_back({3,3,3});
}

void init_dirs(){
	dir_bank.push_back({1,0,0});
	dir_bank.push_back({-1,0,0});
	dir_bank.push_back({0,1,0});
	dir_bank.push_back({0,-1,0});
	dir_bank.push_back({0,0,1});
	dir_bank.push_back({0,0,-1});
	//dir_bank.push_back({0,0,1});
	//dir_bank.push_back({0,0,-1});
}

void hash_test(){
	map<double, EXPR *> population;
	EXPR e;
	e.set_fitness(0.1);
	population.insert({e.get_fitness(),&e});
	for (auto itr = population.begin(); itr!=population.end(); itr++){
		cout<<itr->first<<endl;
	}
	population.erase(0.1);
	cout<<population.size()<<endl;
}

int main(){
	unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
	srand(seed);
	init_dirs();
	init_shapes();

	start();
	//test();
	return 0;
}