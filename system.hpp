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
#include<valarray>

using namespace std;
string TYPE = "EA";


double SIM_TIME = 5;
double DT = 0.001;


double M = 0.1;
double PI = 3.1415926;
int NUM_TRHEAD = 8;
double K = 5000;
double KC = 100000;
valarray<double> g{0,0,-9.8};

double OMEGA = 2*PI;
bool BREATH =true;
long EVAL = 0;

bool DRAW  = true;
int NUM_SYS = 1;
double MUs = 0.1;
double MUk = 0.8;
double DAMP = 0.9999;
//DAMP = 1;
double T = 0;
double SIDE = 0.1;


int LOC_SIZE = 0;
//cube location
//6
vector<valarray<double>> locs = {};
//vector<vector<double>> locs = {{0,0,0}};
vector<valarray<double>> properties{
	//k ,b ,c 
	// k=1000 b=c=0
	// K=20,000 b=c=0
	// K=5000 b=0.25 c=0
	// K=5000 b=0.25 c=pi
	valarray<double>{1000,0,0},
	valarray<double>{20000,0,0},
	valarray<double>{5000,0.2,0},
	valarray<double>{5000,0.2,PI},
};
void prt_arr(valarray<double> arr){
	for (int i =0; i < arr.size(); i++){
		cout<<arr[i]<<", " ;
	}
	cout<<endl;
}

//diffult: how to assgian each cube its char
//ds: cube loc, spring{idx1, idx2, charactors idx[],belong_to cube[]} 

//#pragma omp parallel num_threads(16)
struct Mass{
	double mass  = M;
	valarray<double> pos {0,0,0};
	valarray<double> a{0,0,0};
	valarray<double> v {0,0,0};
};

struct Spring{
	double k = 1;
    double l_init = 0.1;
    double l0 = l_init;
    int idx1 = 1;
    int idx2 = 1;
    double A = 0.1;
    double B = 0.1;
    double w = OMEGA;
    double C = 0;
    unordered_set<int> loc_idx;
};



double dist(valarray<double> v1, valarray<double> v2){
	auto minus = v1-v2;
	auto pow = minus*minus;
	return sqrt(pow.sum());
}

double mag(valarray<double> v){
	auto pow = v*v;
	return sqrt(pow.sum());
}

bool check_outer_rectangel(vector<valarray<double>> rectangle){
	//cout<<rectangle.size()<<endl;
	auto c1 = rectangle[0], c2 = rectangle[1], c3 = rectangle[2];
	// cout<<dist(c1,c2)<<endl;
	// cout<<dist(c3,c2)<<endl;
	// cout<<dist(c1,c3)<<endl;
	// prt_arr(c1);
	// prt_arr(c2);
	// prt_arr(c3);
	//if (dist(c1,c2)> sqrt(2)*SIDE) return false;
	//if (dist(c3,c2)> sqrt(2)*SIDE) return false;
	//if (dist(c3,c1)> sqrt(2)*SIDE) return false;
	return true;
}

class System{
public:
	System(){	
	} 

	System(vector<valarray<double>> locs, vector<int> property_map){
		//auto locs = n.shape();
		vector<vector<valarray<double>>> permitted_spring;
		vector<valarray<double>> loc_set;
		for (int i = 0; i < locs.size(); i++){
			auto l = locs[i];
			valarray<double> points = {0,1};
			vector<valarray<double>> m_in_cube;
			for (auto x : points){
				for (auto y : points){
					for (auto z : points){
						valarray<double> xyz{x,y,z};
						valarray<double> trans{l[0],l[1],l[2]};
						xyz = xyz + trans;
						xyz *= SIDE;
						m_in_cube.push_back(xyz);
						bool has_same = false;
						for (auto & m_loc : loc_set ){
							if ((m_loc==xyz).min()) has_same = true;
						}
						if (!has_same) loc_set.push_back(xyz);
					} 
				}
			}
			//try to add a apring between any of mass in one cube
			for (auto & l1: m_in_cube){
				for (auto & l2: m_in_cube){
					if (! (l1==l2).min()){
						//check if the position of two masses already exist in spring set. 
						//If not, add this pair of location to spring location set
						//to_permitted_spring(permitted_spring,vector<valarray<double>>{l1,l2});
						bool has_same = false;
						for (auto & ps: permitted_spring){
							if ((ps[0]==l1).min() && (ps[1]==l2).min()) has_same = true;
							if ((ps[1]==l1).min() && (ps[0]==l2).min()) has_same = true;
						}
						if (! has_same) permitted_spring.push_back(vector<valarray<double>>{l1,l2});
					}
				}
			}

			auto tmp = m_in_cube.size();
			//cout<<"--------"<<tmp<<endl;
			for (int i=0; i< tmp; i ++){
				for (int j=i+1 ; j < tmp; j ++){
					for (int k = j+1; k < tmp ; k ++){
						vector<valarray<double>> rectangle{m_in_cube[i],m_in_cube[j],m_in_cube[k]};
						//cout<<i<<"  "<<j<<"  "<<k<<endl;
						if (check_outer_rectangel(rectangle)){
							rectangles.push_back(rectangle);
						}
					}
				}
			}
		}

		for (auto & m_loc: loc_set){
			Mass m;
			m.pos = m_loc;
			ms.push_back(m);
			//prt_arr(m.pos);
		}

		for (int i =0; i < ms.size(); i++){
			for (int j =0; j < ms.size(); j++){
				if (i==j) continue;
				bool has_same = false;
				for (auto & ps: permitted_spring){
					if ((ps[0]==ms[i].pos).min() && (ps[1]==ms[j].pos).min()) has_same = true;
				}
				if (!has_same) continue;
				Spring s;
                s.k = K ;
                s.l_init = dist(ms[i].pos,ms[j].pos);
                s.l0 = s.l_init;
                s.idx1 = i;
                s.idx2 = j;
                ss.push_back(s);
			}
		}
		//cout<<"num springs" <<ss.size()<<endl;

		//identif which cube a srping could belong to
		for (auto & s : ss){
			auto loc1 = ms[s.idx1].pos;
			auto loc2 = ms[s.idx2].pos;

			//check back each cube if the spring could belong to
			for (int i = 0; i < locs.size(); i++){
				auto l = locs[i];

				//rebuild the cube again
				valarray<double> points = {0,1};
				vector<valarray<double>> m_in_cube;
				bool find1 = false, find2 = false;
				for (auto x : points){
					for (auto y : points){
						for (auto z : points){
							valarray<double> xyz{x,y,z};
							valarray<double> trans{l[0],l[1],l[2]};
							xyz = xyz + trans;
							xyz *= SIDE;
							if ((loc1 == xyz).min()) find1 = true;
							if ((loc2 == xyz).min()) find2 = true;
						} 
					}
				}
				if (find1 && find2 ) s.loc_idx.insert(i);
			}
		}

		for (auto & rectangle : rectangles){
			vector<int> rect_idx; 
			for (auto & loc: rectangle){
				for (int i = 0; i < ms.size(); i ++){
					if (loc[0]==ms[i].pos[0] && loc[1]==ms[i].pos[1]&&loc[2]==ms[i].pos[2]){
						rect_idx.push_back(i);
					}
				}
			}
			rectangel_idxs.push_back(rect_idx);
		}


		assign(property_map);
		
		double z = 0;
		for (auto & m : ms){
			if (m.pos[2]<z) z = m.pos[2];
		}
		//cout<<"z missing"<<z<<endl;
		translate(valarray<double>{0,0,-z + 0.01});
	}
	void translate(valarray<double> tr){
		for (auto & m : ms){
			m.pos = m.pos + tr;
		}
	}
	void step(double & time){
		vector<valarray<double>> FS;
		//cout<<"start"<<endl; 	
		for (int i =0; i<ms.size(); i++){
            auto & m = ms[i];
            valarray<double> F{0,0,0};
            for (auto & s : ss){
				if (! (s.idx1 == i || s.idx2 == i)) continue ;
                if (BREATH)
                    s.l0 = s.l_init *( 1+ s.B*sin(s.w*time + s.C));
                int start_idx,end_idx;
                if (s.idx1 == i){
                	end_idx = s.idx1;
                    start_idx = s.idx2;
                }
                    
                else{
                	end_idx = s.idx2;
                    start_idx = s.idx1;
                }
                valarray<double> pos_end,pos_start,dirc,unit_dir,delta_l,F_spring;
                pos_end = ms[end_idx].pos;
                pos_start = ms[start_idx].pos;
                dirc = pos_end-pos_start;
                unit_dir = dirc/mag(dirc);        
                delta_l = dirc - s.l0*unit_dir;
                F_spring = -s.k * delta_l ;
                // if (time<0.01){
	               //  cout<<i<< " "<<start_idx << " "<<end_idx<<endl;   
	               //  cout<<s.l0<<endl;
                // 	prt_arr(pos_start);
                // 	prt_arr(pos_end);
                // 	prt_arr(unit_dir);
                // }
                F  = F + F_spring;
            }             
            F = F + m.mass * g;
            valarray<double> F_exter{0,0,0};
            if (m.pos[2] <0){
            	valarray<double> Fz {0,0,-KC*m.pos[2]};
            	F_exter = F_exter + Fz;
            }
            F = F + F_exter;
            //if (m.pos[2] <0 && F_exter[2] >0) F[0] = F[1] = 0;
            //if (m.pos[2]<0) F[0] = F[1] = 0;
            FS.push_back(F);
        }
        for (int i = 0 ; i < ms.size();i++){
        	auto & F = FS[i];
            auto & m = ms[i];
            m.a = F/m.mass;           
			// double mu = 1;
   			double FH = sqrt(F[0]*F[0]+ F[1]*F[1]);
            m.v = m.v + m.a*DT;
            m.v = m.v*DAMP;
            if (m.pos[2]<0) m.v[0] = m.v[1] = 0;
            m.pos = m.pos + m.v*DT;
            //prt_arr(m.pos);
		}
		//add to status
		vector<valarray<double>> m_pos;
		for (auto & m : ms){
			m_pos.push_back(m.pos);
		}
		status.push_back(m_pos);
		time = time + DT;
		//energy();
    }

    void energy(){
    	double Egrav = 0.0, Espring= 0, Ekina = 0;

        for (int i = 0 ;  i< ms.size(); i++){
        	Egrav = Egrav + (-1*ms[i].mass* g[2] * ms[i].pos[2]);
            Ekina = Ekina + 0.5*ms[i].mass*mag(ms[i].v)*mag(ms[i].v);
        }
            
        for (auto & s : ss){
        	auto vec1 = ms[s.idx1].pos;
            auto vec2 = ms[s.idx2].pos;
            double l = dist(vec1,vec2);
            double delta_l = l - s.l0;
            Espring = Espring + 0.5*s.k*delta_l*delta_l;
        }
            
        double e = Egrav+ Espring+Ekina;
        cout<< e <<endl;
    }

	void output_model(){
		string model_file_name = "model.txt";
		ofstream myfile;
		myfile.open (model_file_name);
		myfile<<ms.size()<<endl;
		myfile<<ss.size()<<endl;
		//cout<<rectangel_idxs.size()<<endl;
		myfile<<rectangel_idxs.size()<<endl;
		for (auto & m : ms){
			myfile <<  m.pos[0] << " "<< m.pos[1] << " "<<m.pos[2] <<endl;
		}
		for (auto & s : ss){
			myfile<<s.idx1 << " "<<s.idx2<<endl;
		}
		for (auto & a : rectangel_idxs){
			myfile << a[0]<< " "<< a[1]<< " "<< a[2]<< " "<<endl;
		}
	}

    void output_simul(){
		string status_file_name = "status.txt";
		ofstream myfile;
		myfile.open (status_file_name);
		for (long i = 0; i < status.size(); i +=20){
			for (auto & pos : status[i]){
				myfile <<  pos[0] << " "<< pos[1] << " "<<pos[2] <<endl;
			}
		}
    }

    //property_map :  cube idx to spring property idx
    //properties: spring idx to k,b,c
   	void assign(vector<int> property_map ){
   		//assert(cube_property.size()==ms.size());
   		for (auto & s : ss){
   			valarray<double> avg{0,0,0};
   			for (auto & i : s.loc_idx){
   				int property_idx =  property_map[i];
   				avg = avg + properties[property_idx];
   			}
   			avg /= s.loc_idx.size();
   			s.k = avg[0];
   			s.B = avg[1];
   			s.C = avg[2];
   		}
   	}

   	valarray<double> COG(){
   		valarray<double> ret{0,0,0};
   		for (int i = 0; i < ms.size();i++){
   			ret = ret + ms[i].pos;
   			//prt_arr(ms[i].pos);
   		}
   		ret /= ms.size();
   		//prt_arr(ret);
   		return ret;
   	}
   	//kill if speed varies too much
   	double sim(){
		double time = 0;
		auto COG_0 = COG();
		auto COG_prev = COG_0;
		vector<double> speed; 
		while (1){
			step(time);
			auto COG_now = COG();
			speed.push_back(dist(COG_now,COG_prev));
			COG_prev = COG_now;
			if (time >= SIM_TIME){
				//output_simul();
				//cout<<"output finished simul result"<<endl;
				break;
			}
		}
		auto COG_T = COG();
		// cout<<"---"<<endl;
		// prt_arr(COG_0);
		// prt_arr(COG_T);
		double tot = 0;
		for (auto s : speed){
			tot += s;
		}
		double avg = tot/speed.size();
		double sqr_sum = 0;
		for (auto s: speed){
			sqr_sum += pow(s-avg,2);
		}

		//cout<<sqr_sum<<endl;
		double dist = 0;
		double delta_x = COG_T[0] - COG_0[0];
		double delta_y = COG_T[1] - COG_0[1];
		double delta_z = COG_T[2] - COG_0[2];
		if (sqr_sum > 0.0001) return 0;
		if (delta_z > 0.05) return 0;
		return sqrt(delta_x*delta_x + delta_y*delta_y);
   	}

   	double sim_long(){
		double time = 0;
		auto COG_0 = COG();
		while (1){
			step(time);
			if (time >= SIM_TIME*10){
				//output_simul();
				//cout<<"output finished simul result"<<endl;
				break;
			}
		}
		auto COG_T = COG();
		// cout<<"---"<<endl;
		// prt_arr(COG_0);
		// prt_arr(COG_T);

		double dist = 0;
		double delta_x = COG_T[0] - COG_0[0];
		double delta_y = COG_T[1] - COG_0[1];
		return sqrt(delta_x*delta_x + delta_y*delta_y);
   	}
         
private:
	vector<valarray<int>> spring_idx;  
	vector<Mass> ms;
	vector<Spring> ss;
	vector< vector< valarray<double>>> status;
	vector< vector<valarray<double>>> rectangles;
	vector<vector<int>> rectangel_idxs; 
	void to_permitted_spring(vector<vector<valarray<double>>>  & permitted_spring, 
		vector<valarray<double>> spring_tuple){
		bool has_same = false;
		for (auto & ps: permitted_spring){
			if ((ps[0]==spring_tuple[0]).min() && (ps[1]==spring_tuple[1]).min()) has_same = true;
			if ((ps[1]==spring_tuple[0]).min() && (ps[0]==spring_tuple[1]).min()) has_same = true;
		}
		if (! has_same) permitted_spring.push_back(spring_tuple);
	}
};





bool check_collision(vector<valarray<double>>body, vector<valarray<double>>part){
	for (auto p: part){
		for (auto b: body){
			if ((p==b).min()) return true;}
	}
	return false; 
}
//assemble locs2 into locs1 
vector<valarray<double>> assem_test(vector<valarray<double>>body,vector<valarray<double>>part,int idx1, int idx2, int dir_idx , unordered_map<int, valarray<double>> dir_map){
	vector<valarray<double>> res;
	valarray<double> core = body[idx1];
	valarray<double> cur = part[idx2];
	valarray<double> dif = core - cur;
	for (auto & p : part){
		p+= dif;
	}
	auto dir = dir_map[dir_idx];

	while (check_collision(body, part)){
		for (auto & p : part){
			p += dir;
		}
	}
	for (auto & p: part){
		body.push_back(p);
	}
	return body;
}

/*
int main(){
	
	unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
	srand(seed);
	//cout<<locs.size()<<endl;

	
	
	unordered_map<int, valarray<double>> dir_map;
	dir_map.insert({1,{1,0,0}});
	dir_map.insert({2,{-1,0,0}});
	dir_map.insert({3,{0,1,0}});
	dir_map.insert({4,{0,-1,0}});
	vector<valarray<double>>locs1 = {
		{0,0,10},{0,0,12},{0,0,11}};
	vector<valarray<double>>locs2 = {
		{0,1,0},{0,2,0},{0,3,0}};
	vector<valarray<double>>locs3 = {
		{1,0,0},{0,0,0},{-1,0,0}};
	vector<valarray<double>>locs4 = {
		{0,0,1},{0,0,0},{0,0,-1}};
	locs = assem_test(locs1,locs2,0,2,1,dir_map);
	locs = assem_test(locs,locs3,0,1,2,dir_map);
	locs = assem_test(locs,locs4,1,2,1,dir_map);
	for (auto l : locs) prt_arr(l);
	start();
	//System s;
	// Gene g(5);
	// cout<<g.diversity()<<endl;
}*/