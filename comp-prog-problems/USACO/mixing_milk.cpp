// https://usaco.org/index.php?page=viewproblem2&cpid=855
#include <bits/stdc++.h>
#include <utility>
using namespace std;

int main() {
    vector<pair<int,int>> bkts(3);
    for(int i=0; i<3; i++){
        auto& bk = bkts[i];
        cin >> bk.first >> bk.second;
    }

    for(int i = 0; i<100; i++){
        int _i = i % 3; int _j = (i+1) % 3;
        auto& b1 = bkts[_i]; auto& b2 = bkts[_j];
        int diff = min(b2.first - b2.second, b1.second);
        b2.second += diff; b1.second -= diff;
    }

    for(int i=0; i<3; i++){
        cout<<bkts[i].second<<endl;
    }
}