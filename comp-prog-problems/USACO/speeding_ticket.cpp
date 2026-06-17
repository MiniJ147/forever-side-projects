// https://usaco.org/index.php?page=viewproblem2&cpid=568
#include <bits/stdc++.h>
using namespace std;

int main() {
	int N, M; cin >> N >> M;
    vector<pair<int,int>> roads(N);
    for(int i=0; i<N; i++){
        cin >> roads[i].first >> roads[i].second;
    }

    int curr = 0; int ans = 0;
    for(int i=0; i<M; i++){
        int dist, speed; cin >> dist >> speed;
        while(dist){
            auto& seg = roads[curr];
            ans = max(ans, speed - seg.second);
            if(dist < seg.first){
                seg.first -= dist;
                break;
            }
            dist -= min(dist, seg.first);
            curr += 1;
        }
    }

    cout << ans;
    return 0;
}