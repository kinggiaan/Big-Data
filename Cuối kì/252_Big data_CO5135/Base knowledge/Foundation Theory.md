# 1. Search Engine  
## How google work
Đầu tiên mình nhận ra là khi search GG sẽ trả kết qủa crawler từ nội dung web về chứ không phải gg chứa sẵn bản xếp hạng ranking các web liên quan, đến từ mình của search từ ban đầu.

### Flow của 1 search engine:
 Crawler -> Index -> Ranking (Query)
B1: Crawler như gg sẽ có bot chạy liên tục 24/24 để lấy thông tin từ các trang web về content của web, ảnh , ... Hiện nay các website đang optimize cho search enginer của GG.
Bot của gg sẽ đọc file robots.txt để biết trang nào được phép crawler về và sau đó index

B2: Index là sẽ phân tích content của web  như media, title của web, structure của web ra sao. Cũng như sẽ xác định xem content này có bị trùng với content đã có hay chưa từ database hổng lồ của mình. Nếu trùng thì sẽ bỏ qua vào ko đưa vào

B3: Ranking là bước quan trọng vì search sẽ phân tích ý định tìm kiếm ban đầu của bạn và đưa các thông tin liên quan đến điều bạn đang tìm kiếm, trước đi đưa cho bạn xem thì nó sẽ xếp hạng mức độ liên quan giữa thông nó có và thông tin bạn muốn tìm.
TH GG sẽ có thêm rất nhiều factor khác ảnh hưởng tới như location, privacy, time, ...

### Vậy back lại topic của mình, vậy 3 bước này sẽ ra sao?

B1: Phân tích thông tin có từ Arvix, từ metadata, title, ngành, abstract của bài báo rồi chuyển thành vector hả?
B2: Lưu các vector đó lại vào 1 nơi chứa và cần có chiến lược để chứa lượng thông tin lớn từ các bài báo
B3: input search vào và sẽ đi tìm và so sánh với các bài báo hiện có.

### Câu hỏi đặt ra là:
1. Tại sao lại gợi là hyper search? Mình hiểu là vector search và sql search chung vì sql sẽ hỗ trợ search theo metadata còn vector sẽ hỗ trợ search theo abstract. Mỗi cách search có uus điểm và khuyết điểm của mình, hyper search sẽ bổ trợ nhau để đưa ra kết quả chính xác hơn. 
2. Vậy cụ thể bài toán của mình đang là gì? Nó nằm trong scope nào? Có ai đã làm chưa và làm như thế nào? Mình có thể làm 1 phần nhỏ ra sao trong đó.

# 2. Bài toán Match
Tại sao gõ "Học máy" lại tìm ra "Machine Learning"? (Hiểu khái niệm Tokenization, Stop words, Lemmatization / Stemming).
Sau khi hiểu ra các kiến thức đã học [[NLP]]  thì mình hiểu việc mình chia word by word là đang Tokenization, STop words là đưa các từ, dấu không có ý nghĩa trong câu ra khỏi câu để xử lý, Lemmation/Steamming là rút gọn từ về các dạng nguyên bảng hơn như "running" thì "run"
Tóm lại, chúng đều ra kĩ thuật pre processing trong NLP, nhưng câu hỏi ban đầu là tại sao "Học máy" lại search ra đưuọc "Machine learning"

Vậy thì khi pre process xong qua bước process, nghĩa là chuyển văn bản về dạng vector rồi khi tìm kiếm 2 ngôn ngữ của 1 từ sẽ ở dạng gần nhau hả?

Sau khi hỏi Gemni, mình hiểu là nó nằm ở Semantic presentaion và Multi langue cross??
Nghĩa là khi 1 mô hình được train trên dữ liệu đa ngôn ngữ, chúng ta sẽ biểu diễn dưới dạng vector rồi sau đó so sanh khoảng các bằng cos sin thì khoảng cách ~ 1, nên chứng được xem là giống nhau.

## Câu hỏi đặt ra là:
1. Nghĩa là phải có 1 đống kiến thức, tri thức trước đó rồi mới phần Semantic presetation và multi languega cross. Vậy thì mình sẽ phải hiểu tiếp tại sao có 2 từ khóa này và tập train ra 1 cái của riêng mình không nhỉ?
2. Sau khi liên kết môn này và NLP mình cảm thấy sự liên kết giữa các môn học chứ không bị rời rạc nữa, từ đó mình càng hiểu thêm tại sao phải vững base của ngành
3. Vậy lúc này sự big data của dự án nằm ở số lượng bài báo khổng lồ và các mình xử lý chúng làm sao cho nhanh và chính xác nhỉ (Volume và Velocity - Accuracy)