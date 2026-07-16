Link for slide: [[slide5-recsys-full-BK-v2.pdf]]

Mục tiêu của reomendation system:
1. Thông qua hệ thống gợi ý, giúp hệ thống gợi ý tới người dùng nhuwgx sản phẩm hầu như không ai quan tâm. 
   TH những sp có giá trị cao những ít người biết tới như cuốn sách Touching the void -> Into Thin Air
2.

# Các kiểu Recommendations
## 1. Editorial and hand curated 
- Danh sách yêu thích
- Danh sách danh mục thiết yếu
## 2. Simple aggregates
* Top 10
* Most popular
* Recent uploads
## 3. Talored to invidual users
* Amazon
* Netflix
# Formal Model
Dựa theo sự yêu thích của người dùng, như FB có reaction nhưu like, love, sad, ...
![[Pasted image 20260312182421.png]]

## Utility matrix 
![[Pasted image 20260312182500.png]]
## Key Problems 
Dựa trên Utility atrix thì có thể thấy là data khá Thưa, không đầy đủ tất cả các cột,
1. Dựa theo cac cột đã có
2. Dự đoán các ô chưa được điền từ những người khác
3. ... 
## Gathering ratings
Khó mà yêu cầu người dùng đánh giá 
Hay dùng các cho xu hay phần thưởng khi đánh giá, hoặc học từ action của ngwuoif dùng 

## Extrapolating utilities
> (Ngoại suy giá trị tiện ích) dùng để chỉ bài toán cốt lõi: dự đoán mức độ quan tâm hoặc đánh giá của người dùng đối với những sản phẩm mà họ chưa từng tương tác

**Problem**: khi mà người dùng hầu như chưa có đánh giá hầu hết các sản phẩm
-> Cold start : New items, New users
.


Solution: tiếp cận theo 3 hướng khác
1. Content : tương tự thế nào với các sản phẩm khác
2. Collaborative : dưa theo những người giống với user này , vd 2 user có chung sở thích 
3. Latent factor based: 

### Content-based Recommendation
Main idea: gợi ý sản phẩm tới **customer x** giống với sản phẩm trước đây được **đánh giá cao** bởi x

Cách hiện thực theo plan:
![[Pasted image 20260312183402.png]]

# Exercise

Three computers, A, B, and C, have the numerical features listed below:

| Feature              | A   | B   | C   | D   | E   |
| -------------------- | --- | --- | --- | --- | --- |
| **Processor speed**  | 3   | 2.5 | 2.8 | 2   | 2.9 |
| **Disk size**        | 500 | 320 | 640 | 350 | 580 |
| **Main-memory size** | 6   | 4   | 6   | 4   | 6   |
| **Rating of user x** | 4   | 2   | 5   | ?   | ?   |

A certain user x has rated the three computers as follows: A: 4 stars, B: 2 stars, C: 5 stars. No ratings for D, E

* Compute a user profile for the user x, with components for processor speed, disk size, and main memory size
* Does user like D and E? (Calculate the cosine similarity between user profile and item profile)

Dựa theo slide thì cô có đưa ra 3 example, và áp dụng example 3 để giải bài này



## tìm similar user 
![[Pasted image 20260312190338.png]]
Problem của cách 1 là sẽ bị thiếu rating và bỏ qua
Cách 2 là coi 0 đánh giá là negative, dislike
Cách 3 thì hiệu quả nhất trong 3 vì đưa về chung 1 vector vì mỗi user có cách đánh giá khác nhau max 4 hoặc max 3 nhưng về chung thì giống nhau

Bài toán thực tế 
![[Pasted image 20260312190620.png]]
Thấy rõ là pearson phù hợp nhất vì chỉ rõ sự khác biệt giữa 2 user

## Rating prediction
Sau khi xác định được những user giống nhau, giờ qua dựa đoán rating từ tập đó 
Key: trên đây chỉ có sự xuất hiện của user và rating, ko có feature của sản phẩm, bài toán đơn giản hơn

# Complexity
Khi làm các bài toán này rất lớn  
• Expensive step is finding k most similar customers: O(|X|) 
• Too expensive to do at runtime: Could pre-compute 
• Naïve pre-computation takes time O(k ·|X|) 
	• X … set of customers 
• We already know how to do this! 
	• Near-neighbor search in high dimensions (LSH) 
	• Clustering 
	• Dimensionality reduction

Gợi ý bài toán thực tế: [Netflix Prize - Wikipedia](https://en.wikipedia.org/wiki/Netflix_Prize)
![[Pasted image 20260312192505.png]]
# Latent Factor model
Không phải là giải pháp đơn mà có thể chiến thắng được cuộc thi The Netflix Prize. Họ đã phải dùng nhiều giải pháp kết hợp để đạt được 10% đó, trầy trật

Không gian tiềm ẩn