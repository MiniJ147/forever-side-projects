// https://usaco.org/index.php?page=viewproblem2&cpid=664
#include <bits/stdc++.h>
using namespace std;

int main() {
	int N; cin >> N;
    int C[26] = {0};
    for(int i=0; i<N; i++){
        int A[26] = {0}; int B[26] = {0};
        string w1, w2; cin >> w1 >> w2;

        for(char c : w1){ A[c-97] += 1; }
        for(char c : w2){ B[c-97] += 1; }
        for(int j=0; j<26; j++){ C[j] += max(A[j], B[j]); }
    }
    
    for(int i=0; i<26; i++){ cout<<C[i]<<endl;}
    return 0;
}
