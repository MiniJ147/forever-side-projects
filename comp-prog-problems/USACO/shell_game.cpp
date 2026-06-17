// https://usaco.org/index.php?page=viewproblem2&cpid=891
#include <bits/stdc++.h>
using namespace std;

int main() {
	int N; cin >> N;
    vector<int> shell_pos(3);
    for(int i=0; i<3; i++) shell_pos[i] = i;

    vector<int> counter(3);
    while(N--){
        int a, b, g; cin >> a >> b >> g;
        a--, b--, g--;

        swap(shell_pos[a], shell_pos[b]);
        counter[shell_pos[g]]++;        
    }
    cout << max({counter[0], counter[1], counter[2]});
}
