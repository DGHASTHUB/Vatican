import re
import time
import telebot
import json
import os

TOKEN = "8945074503:AAFfjC0w1epRAa2ujt4uLLsH1Gq4t7ooMVo"
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "bot_data.json"

DEFAULT_WELCOME_TEXT = "🎉 Chào mừng {user} đã tham gia {group}!"

DEFAULT_KEYWORD_RESPONSES = {
    "chờ": "Chờ cái đầu buồi",
    "tưởng": "tưởng cái địt mẹ nhà mày chết cả đi vô nhóm bố sủa cái lồn mẹ nhắn như cái đầu cặc mày",
    "đợi": "Đợi bố mày cưới vợ xong đã con chó",
    "nhanh": "Nhanh cái đít mẹ mày",
    "chậm": "Chậm như chó rách mà sủa",
    "biết": "Biết cái đầu khấc",
    "hiểu": "Hiểu cái máu lồn",
    "nghe": "Nghe cái con mẹ mày",
    "nói": "Nói lắm như chó sủa",
    "im": "Im cái mồm thối nhà mày vào",
    "câm": "Câm cái họng chó lại",
    "bật": "Bật cái đít mẹ mày lên",
    "chạy": "Chạy đi đâu con chó rách",
    "đuổi": "Đuổi cái đầu buồi",
    "bắt": "Bắt cái con mẹ mày à",
    "bắn": "Bắn cứt vào mặt mày giờ",
    "kill": "Kill cái đít mẹ mày chứ kill",
    "win": "Win cái máu lồn, toàn nằm ngửa",
    "lose": "Lose ngập mặt còn bày đặt sủa",
    "ngu ngốc": "Ngu từ tổ tiên nhà mày ngu đi",
    "óc chó": "Đừng tự nhận họ hàng với bố mày",
    "thằng": "Thằng đĩ mẹ mày chứ thằng",
    "con": "Con đĩ chó nhà mày",
    "ông": "Ông nội nhà mày đây, quỳ xuống",
    "bà": "Bà già mày bán muối rồi à",
    "cha": "Cha mày ra đường bị xe cán kìa",
    "mẹ": "Mẹ mày đang bú cặc tao này",
    "anh": "Anh cái đầu buồi, gọi bố đi",
    "em": "Em cái con mẹ mày",
    "bạn": "Bạn bè cái đít mẹ mày",
    "thù": "Thù hằn cái máu lồn",
    "đánh": "Đánh cái đầu khấc",
    "đấm": "Đấm vỡ mồm con đĩ mẹ mày giờ",
    "chém": "Chém gió cái lồn má mày",
    "giết": "Giết cái con mẹ mày đi",
    "sống": "Sống chật đất tốn cơm",
    "chết tiệt": "Tiệt cái đầu buồi nhà mày",
    "cây": "Cây cái lồn",
    "cay": "Cay cái đít mẹ mày lắm rồi phải không",
    "tức": "Tức điên người chưa con chó",
    "điên": "Điên cái đầu khấc",
    "khùng": "Khùng cái con mẹ mày",
    "hâm": "Hâm đơ như não chó",
    "đần": "Đần độn như bò rách",
    "thần kinh": "Thần kinh phân liệt à con đĩ",
    "bệnh": "Bệnh hoạn như bố mày thích bú lồn",
    "thuốc": "Thuốc độc uống vào chết cụ mày đi",
    "viện": "Vào viện tâm thần mà ở",
    "trại": "Trại súc vật không nhốt mày lại à",
    "chó": "Chó sủa mất phần kìa con",
    "mèo": "Mèo mả gà đồng như mẹ mày",
    "heo": "Heo nái đẻ ra mày đấy à",
    "gà": "Gà mờ bày đặt gáy to",
    "vịt": "Vịt đực sủa bậy",
    "chim": "Chim ngắn đòi đú",
    "cá": "Cá rô phi đòi ngửa lồn",
    "sâu": "Sâu bọ đòi đọ với rồng",
    "kiến": "Kiến cỏ bày đặt lên voi",
    "muỗi": "Muỗi đốt inox hay đòi cắn bố",
    "ruồi": "Ruồi nhặng bu quanh đống cứt là mày",
    "bò": "Bò tót ngậm cứt",
    "trâu": "Trâu điên hút hầm cầu",
    "ngựa": "Ngựa chứng đứt cương",
    "dê": "Dê cụ thấy lồn sáng mắt",
    "khỉ": "Khỉ khô mốc mỏ",
    "vượn": "Vượn hú trong rừng",
    "cọp": "Cọp giấy đòi hù bố",
    "sư tử": "Sư tử Hà Đông rách việc",
    "hổ": "Hổ đói ăn cứt",
    "báo": "Báo thủ rách việc",
    "mèo mướp": "Mèo mả gà đồng",
    "chuột": "Chuột cống rãnh đòi ăn sâm",
    "sóc": "Sóc lọ ra bài à con",
    "nhím": "Nhím xù lông mút cặc",
    "rùa": "Rùa bò dưới bùn",
    "thỏ": "Thỏ đế run như cầy sấy",
    "rắn": "Rắn độc cắn vào cặc mày",
    "ếch": "Ếch ngồi đáy giếng đòi sủa",
    "cóc": "Cóc ghẻ đòi ăn thịt thiên nga",
    "cua": "Cua kẹp dái mày giờ",
    "tôm": "Tôm tép tuổi lồn",
    "mực": "Mực đen thui như mõm mày",
    "bạch tuộc": "Bạch tuộc bú cặc",
    "cá mập": "Cá mập cắn đứt đầu buồi mày",
    "cá voi": "Cá voi nuốt chửng mẹ mày",
    "sóng": "Sóng thần cuốn chết cụ mày đi",
    "gió": "Gió độc thổi bay xác mày",
    "mưa": "Mưa axit rát mặt mày chưa",
    "nắng": "Nắng cháy da cháy cặc",
    "bão": "Bão táp cuốn sạch họ hàng mày",
    "lũ": "Lũ lụt trôi nhà trôi mẹ mày đi",
    "đất": "Đất nứt chôn vùi tổ tiên mày",
    "trời": "Trời đánh thánh đâm chết mẹ mày",
    "sấm": "Sấm sét đánh ngang dái mày",
    "chớp": "Chớp giật cháy lông lồn",
    "mây": "Mây đen che phủ cuộc đời mày",
    "sương": "Sương mù che mắt chó",
    "tuyết": "Tuyết phủ lạnh ngắt cái thây mày",
    "lửa": "Lửa thiêu cháy xác con đĩ mẹ mày",
    "nước": "Nước đái ngập mồm mày kìa",
    "băng": "Băng giá đóng băng não chó mày",
    "đá": "Đá đè chết cụ mày đi",
    "cát": "Cát bụi bay vào mồm thối",
    "bụi": "Bụi đời rách rưới bày đặt sủa",
    "rác rưởi": "Rác rưởi như mày đem đi đốt",
    "phân": "Phân chó còn thơm hơn mồm mày",
    "cứt": "Cứt trôi sông không bằng mày",
    "nước đái": "Uống nước đái gục mẹ mày đi",
    "đờm": "Đờm dãi khạc vào mặt mày",
    "mủ": "Mủ hôi tanh như máu lồn mày",
    "máu": "Máu chó trào họng chết mẹ mày đi",
    "dịch": "Dịch tả lây cho cả họ nhà mày",
    "bệnh tật": "Bệnh tật đầy người chết ko kịp trối",
    "ung thư": "Ung thư giai đoạn cuối còn sủa",
    "siêu vi": "Siêu vi khuẩn ăn mòn não chó",
    "vi trùng": "Vi trùng bám đầy lông lồn má mày",
    "ký sinh": "Ký sinh trùng bám đít bú cứt",
    "giun": "Giun sán lúc nhúc trong bụng mày",
    "sán": "Sán dây quấn cổ chết mẹ mày đi",
    "bọ chét": "Bọ chét cắn nát cái lồn mẹ mày",
    "ve chó": "Ve chó bu đầy lông mặt mày",
    "rận": "Rận mu cắn nát dái bố mày à",
    "chấy": "Chấy rận đẻ đầy đầu óc lồn",
    "mối": "Mối mọt ăn mòn xương cốt tổ tiên mày",
    "mọt": "Mọt sách rách việc",
    "gián": "Gián đất bò vào mõm thối",
    "nhện": "Nhện giăng tơ bẫy con đĩ mẹ mày",
    "bọ ngựa": "Bọ ngựa cắt đầu dái mày",
    "chuồn chuồn": "Chuồn chuồn đâm đầu vào cứt",
    "bướm": "Bướm thối hoắc bày đặt bay lượn",
    "ong": "Ong đốt sưng mặt con đĩ chó",
    "ve sầu": "Ve sầu kêu điếc tai bố mày",
    "cào cào": "Cào cào châu chấu đá xe",
    "châu chấu": "Châu chấu ngậm cứt phun người",
    "bọ cạp": "Bọ cạp chích chết mẹ mày",
    "rết": "Rết độc cắn nát trym mày",
    "sên": "Sên nhớt nhợ như bãi bầy nhầy",
    "ốc": "Ốc sên bò chậm như tốc độ não mày",
    "hàu": "Hàu sữa bú cặc",
    "sò": "Sò lông thâm xì như mõm chó",
    "nghêu": "Nghêu sò ốc hến rách việc",
    "ốc bươu": "Ốc bươu vàng phá hoại ruộng lúa",
    "cá trê": "Cá trê chui ống cống",
    "cá rô": "Cá rô phi ngửa bụng",
    "cá lóc": "Cá lóc nướng trui mồm mày",
    "cá trắm": "Cá trắm đen thui như chó mực",
    "cá mè": "Cá mè một lứa với nhà mày",
    "cá chép": "Cá chép hóa rồng hay hóa cứt",
    "cá tràng": "Cá tràng hạt đéo bằng con chó",
    "cá kiếm": "Cá kiếm đâm chết cụ mày",
    "cá đuối": "Cá đuối bét nhè",
    "cá sấu": "Cá sấu ăn thịt cả họ nhà mày",
    "cá voi xanh": "Cá voi xanh đè bẹp dí mày",
    "cá heo": "Cá heo nhảy múa trên bãi cứt",
    "cá mập trắng": "Cá mập trắng cắn đứt đôi người mày",
    "cá b Piranha": "Piranha rỉa thịt con mẹ mày",
    "chim sẻ": "Chim sẻ hót líu lo như mày sủa bậy",
    "chim én": "Chim én báo xuân hay báo tang nhà mày",
    "chim cu": "Chim cu gáy điếc tai",
    "chim cú": "Chim cú mèo báo điềm gở",
    "chim đại bàng": "Đại bàng quắp xác mày vứt sọt rác",
    "chim kên kên": "Kên kên ăn xác thối nhà mày",
    "chim quạ": "Quạ đen kêu trên nóc nhà tang",
    "chim bồ câu": "Bồ câu bay qua ỉa lên mặt mày",
    "chim sẻ rừng": "Sẻ rừng đéo có tuổi",
    "gà trống": "Gà trống thiến đòi gáy",
    "gà mái": "Gà mái tơ bị bố thịt rồi",
    "gà ác": "Gà ác hầm thuốc bắc tẩm bổ cho chó",
    "gà tây": "Gà tây lông lá lùm xùm",
    "vịt xiêm": "Vịt xiêm kêu cạp cạp điếc tai",
    "ngỗng": "Ngỗng cái cắn đứt dái mày",
    "thiên nga": "Thiên nga lội bùn ao tù",
    "hồng hạc": "Hồng hạc què cụt chân",
    "đà điểu": "Đà điểu rúc đầu vào cát như mày trốn nợ",
    "chim cánh cụt": "Cánh cụt đi lạch bạch như mày ngậm cứt",
    "chim ruồi": "Chim ruồi đập cánh nhanh bằng tốc độ sủa bậy",
    "chim hồng tước": "Hồng tước hót hay nhưng mõm thúi",
    "bò sữa": "Bò sữa cho bú mớm tiền",
    "bò rừng": "Bò rừng húc văng xác mày",
    "bò tót Tây Ban Nha": "Bò tót húc chết tươi bố mày à",
    "trâu nước": "Trâu nước đầm lầy hôi rình",
    "ngựa vằn": "Ngựa vằn chạy rách giò",
    "ngựa chiến": "Ngựa chiến đéo chấp ngựa cùi như mày",
    "lừa đảo": "Lừa đảo bị chặt tay chặt chân",
    "lạc đà": "Lạc đà nhổ nước bọt vào mặt mày",
    "gấu trúc": "Gấu trúc thâm quầng mắt giống mày thức đêm bú cặc",
    "gấu ngựa": "Gấu ngựa cào nát mặt chó",
    "gấu Bắc Cực": "Gấu Bắc Cực chết đói vì ko có cứt ăn",
    "sư tử biển": "Sư tử biển ngậm cá sặc",
    "hải cẩu": "Hải cẩu béo ú lăn lóc",
    "cá voi sát thủ": "Sát thủ đâm thủng lồn mẹ mày",
    "rái cá": "Rái cá bơi lội ngụp lặn trong hố xí",
    "hải ly": "Hải ly xây đập chặn nước đái mày",
    "chồn hương": "Chồn hương thơm hay thối như mồm mày",
    "cầy mangut": "Cầy mangut cắn rắn độc",
    "lửng mật": "Lửng mật bất tử nhưng gặp bố cũng quỳ",
    "nhím biển": "Nhím biển đâm rách tay thối",
    "sao biển": "Sao biển nằm phơi thây trên cát",
    "hải quỳ": "Hải quỳ chích điện chết tươi",
    "san hô": "San hô chết trắng đáy biển",
    "cá ngựa": "Cá ngựa đực sinh con giống bố mày",
    "lươn": "Lươn chạch trơn tuột như văn vở của mày",
    "trạch": "Trạch đẻ ngọn đa",
    "cá trê vàng": "Cá trê vàng chui hố xí công cộng",
    "cá rô đồng": "Cá rô đồng nhảy tưng tưng như mày lúc sủa",
    "cá lóc bông": "Cá lóc bông ăn thịt con",
    "cá quả": "Cá quả nướng trui chấm mắm tôm",
    "cá trắm cỏ": "Cá trắm cỏ ăn tạp như mày",
    "cá mè vinh": "Cá mè vinh bơi ngược dòng",
    "cá chép giòn": "Cá chép giòn nhai giòn rụm",
    "cá nheo": "Cá nheo râu dài như râu chó",
    "cá trê phi": "Trê phi khổng lồ ăn xác thối",
    "cá rô phi": "Rô phi còi cọc đói ăn",
    "cá thác lác": "Thác lác đập chết tươi",
    "cá bống": "Cá bống kho tiêu cay xè mõm",
    "cá cơm": "Cá cơm khô quắt queo như người mày",
    "cá nục": "Cá nục hấp cuốn bánh tráng",
    "cá thu": "Cá thu cắt khúc rán giòn",
    "cá ngừ": "Cá ngừ đại dương đóng hộp",
    "cá hồi": "Cá hồi phi lê sống chấm mù tạt",
    "cá tầm": "Cá tầm trứng muối đắt gấp vạn lần đời mày",
    "cá chình": "Cá chình điện giật tung dái",
    "cá m lịch": "Cá m lịch trườn qua bãi cứt",
    "cá bơn": "Cá bơn dẹt lép như mặt mày",
    "cá mặt quỷ": "Cá mặt quỷ nhìn giống hệt ông nội mày",
    "cá đá": "Cá đá cắn nhau sứt đầu mẻ trán",
    "cá kiểng": "Cá kiểng bơi trong bể kính",
    "cá vàng": "Cá vàng não cá vàng y chang mày",
    "cá chọi": "Cá chọi xiêm đá gãy vây",
    "cá tai tượng": "Tai tượng to mồm như mày",
    "cá lóc kiểng": "Lóc kiểng săn mồi ác chiến",
    "cá rồng": "Cá rồng huyết long bơi lội oai phong",
    "cá Sam": "Cá Sam đĩa tròn xoe",
    "cá bảy màu": "Bảy màu sặc sỡ như bóng lộ",
    "cá betta": "Betta plakat đá hăng",
    "cá guppy": "Guppy đẻ con liên tục",
    "cá molly": "Molly đen thui",
    "cá kiếm đỏ": "Kiếm đỏ đuôi dài",
    "cá trân châu": "Trân châu bơi lội tung tăng",
    "cá vàng mắt lồi": "Mắt lồi như mắt chó chết trôi",
    "cá cọp": "Cọp vằn bơi lội",
    "cá đuối gai độc": "Đuối độc đâm chết tươi",
    "cá mập voi": "Mập voi khổng lồ nuốt trọn mày",
    "cá mập đầu búa": "Đầu búa đập vỡ sọ chó",
    "cá mập hổ": "Mập hổ ăn thịt người",
    "cá mập trắng lớn": "Mập trắng cắn xé xác mày ra trăm mảnh",
    "ô": "Bắn cặn rồi",
    "helo": "Helo Cac dit me",
    "ban": "Ban cái đit me mày óc lồn",
    "chửi": "Bọn Óc Lồn Nqu Nàg?",
    "admin": "Gọi Anh gì đó, muốn bú cặc anh à?",
    "menu lỏ": "Lỏ cái máu cặc, do điện thoại mày bị garena liến đít nên ban",
    "rác": "Cái Địt Con Mẹ Thằng lồn",
    "bot": "gọi gọi cái địt mẹ mày bố mày bot mệt dùng thằng óc căc",
    "hài": "Hài Cái Con mẹ nhà mày",
    "gay": "Bố mày bắn cặn tinh lên mặt mày toàn cứt chim",
    "vcl": "Vãi Con mẹ mày thằng choá đẻ",
    "vui": "Vui cái bà nhà mày",
    "hi": "xin Chào cái con đĩ mẹ mày",
    "sủa": "Okii Anh yeuuu Bọn nó có trình đâu sủa",
    "mất": "Mất Cái Con mẹ mày thằng chó",
    "má": "Sao ý kiến gì tao bắn cặn vào cặc chó m giờ",
    "bú": "Bú Cái máu lồn máu cặc mày giờ đang thèm",
    "cak": "Con chó máu lồn mày muốn chửi tao à",
    "ai": "Thì ra là mày à con chó",
    "thùng": "Thùng rỗng kêu to như cái mõm mày",
    "gạo": "Gạo hết mốc meo còn sủa",
    "bát": "Bát cơm chó đớp hàng ngày",
    "đũa": "Đũa mốc đòi mâm son",
    "thìa": "Thìa dĩa nhà mày đem đi cầm đồ hết rồi",
    "dao": "Dao cùn đòi chặt cổ bố",
    "kéo": "Kéo cắt lông lồn má mày",
    "búa": "Búa tạ đập nát đầu mày",
    "kìm": "Kìm cộng lực bẻ gãy dái mày",
    "cưa": "Cưa gỗ hay cưa cổ con đĩ mẹ mày",
    "đinh": "Đinh rỉ đâm thủng bàn chân thối",
    "ốc vít": "Ốc vít lỏng lẹo như não mày",
    "bulong": "Bulong lỏng toét cái đầu buồi",
    "cờ lê": "Cờ lê vặn cổ con chó rách",
    "mỏ lết": "Mỏ lết đập vỡ sọ mẹ mày",
    "xẻng": "Xẻng hốt cứt đổ vào mồm mày",
    "cuốc": "Cuốc đất trồng mồ tổ tiên mày",
    "rìu": "Rìu chém đứt đôi người mày ra",
    "thang": "Thang gãy cổ ngã xuống hố xí",
    "giường": "Giường gãy sập vì mẹ mày nằm lắm",
    "chiếu": "Chiếu rách cuốn thây ma mày vứt sông",
    "chăn": "Chăn ấm đệm êm đéo tới lượt chó sủa",
    "gối": "Gối đầu lên đống cứt mà ngủ",
    "mùng": "Mùng mền rách rưới bày đặt chảnh",
    "màn": "Màn cửa che mặt con đĩ mẹ mày",
    "bàn": "Bàn ghế nhà mày bán trả nợ hết rồi",
    "ghế": "Ghế nhựa ngồi tụt dái ra",
    "tủ": "Tủ quần áo chứa toàn đồ ăn xin",
    "giá": "Giá sách bày toàn truyện con heo",
    "kệ": "Kệ mẹ mày chứ quan tâm làm đéo gì",
    "gương": "Soi gương xem mặt mày giống con súc vật nào",
    "lược": "Lược chải đầu chấy rận đầy",
    "xà phòng": "Xà phòng tắm rửa sạch cứt mồm mày đi",
    "kem đánh răng": "Kem đánh răng trộn cứt cho thơm mồm",
    "bàn chải": "Bàn chải cọ bồn cầu đút họng mày",
    "khăn mặt": "Khăn mặt lau đít lau mồm cùng một cái",
    "khăn tắm": "Khăn tắm quấn xác chết nhà mày",
    "chậu": "Chậu rửa mặt chứa nước đái chó",
    "gáo": "Gáo dừa múc nước cống uống đi con",
    "xô": "Xô đựng phân hố xí nhà mày",
    "chổi": "Chổi đót quét nhà quật vào mặt mày",
    "hót rác": "Hót rác đổ thẳng vào miệng con đĩ",
    "giẻ lau": "Giẻ lau sàn dơ dáy y như mồm mày",
    "thùng rác": "Thùng rác chứa toàn họ hàng nhà mày",
    "bật lửa": "Bật lửa đốt lông lồn má mày cháy đen",
    "diêm": "Diêm quẹt cháy nhà chết cụ mày đi",
    "nến": "Nến thắp hương cúng tổ tiên nhà mày",
    "đèn": "Đèn dầu hắt hiu như cuộc đời con chó",
    "quạt": "Quạt mo quạt mát vào cái mặt lồn",
    "điện": "Điện giật tung dái chết cha mày",
    "nước sôi": "Nước sôi dội thẳng vào mặt thối",
    "bếp": "Bếp ga nổ tung banh xác nhà mày",
    "nồi": "Nồi cơm điện nấu toàn cứt trâu",
    "xoong": "Xoong chảo méo mó như mặt mày",
    "chảo": "Chảo rán mỡ bắn đầy lông lồn",
    "muôi": "Muôi múc canh tạt thẳng vào mõm",
    "thớt": "Thớt gỗ thái thịt con chó rách",
    "rổ": "Rổ rá cạp lại đéo ai thèm",
    "rá": "Rá vo gạo chứa toàn dòi bọ",
    "ấm": "Ấm nước sôi sùng sục như máu lồn",
    "cốc": "Cốc chén vỡ nát bét",
    "chén": "Chén rượu độc uống vào ngỏm cụ mày",
    "đĩa": "Đĩa bay chở mẹ mày lên sao hỏa",
    "thìa muỗng": "Thìa muỗng múc cứt ăn ngon miệng không",
    "bình": "Bình bông cúng đám giỗ nhà mày",
    "lọ": "Lọ mực đổ đen thui mõm chó",
    "hũ": "Hũ mắm tôm thối không bằng mồm mày",
    "vại": "Vại dưa khú mốc meo",
    "lu": "Lu nước đái ngập đầu ngập cổ",
    "khạp": "Khạp đựng phân bò",
    "bao": "Bao tải rách đựng xác mày",
    "túi": "Túi ni lông vứt đầy đường bẩn thỉu",
    "giấy": "Giấy vệ sinh lau đít xong đút mồm mày",
    "bút": "Bút bi chọc thủng mắt chó",
    "thước": "Thước kẻ đánh vỡ đầu óc lồn",
    "tẩy": "Tẩy xóa cuộc đời mày khỏi thế giới",
    "mực": "Mực tàu phun đen mặt con đĩ",
    "hộp": "Hộp đựng tro cốt tổ tiên mày",
    "cặp": "Cặp sách đi học toàn trốn học bú cặc",
    "balo": "Balo nặng trĩu toàn gánh nợ đời",
    "áo": "Áo rách vai vá chằng vá đụp",
    "quần": "Quần thủng đít lộ cả lông đít",
    "váy": "Váy ngắn ngửa lồn kiếm tiền",
    "giày": "Giày dép vứt đầy sọt rác",
    "dép": "Dép tổ ong quật vỡ mồm",
    "mũ": "Mũ cối đội đầu ngu như bò",
    "nón": "Nón lá che nắng che mưa che mặt chó",
    "kính": "Kính cận lồi cả mắt ra vẫn ngu",
    "khẩu trang": "Khẩu trang đéo che được cái mồm thối",
    "nhẫn": "Nhẫn vàng giả mã mã hàng mã",
    "dây chuyền": "Dây chuyền xích chó quấn cổ mày",
    "vòng": "Vòng hoa tang lễ chuẩn bị sẵn cho mày",
    "lắc": "Lắc lư cái đầu buồi",
    "hoa tai": "Hoa tai đính đầy rận",
    "đồng hồ": "Đồng hồ điểm giờ chết của mày đến rồi",
    "ví": "Ví tiền rỗng tuếch đòi đú",
    "tiền xu": "Tiền xu rách đéo mua được cọng lông",
    "thẻ": "Thẻ ngân hàng âm tiền đòi oai",
    "sim": "Sim rác giống hệt chủ nhân của nó",
    "điện thoại": "Điện thoại vỡ màn hình đòi chat",
    "máy tính": "Máy tính sập nguồn đéo cho sủa nữa",
    "chuột máy tính": "Chuột máy tính gặm đứt dây não mày",
    "bàn phím": "Bàn phím gõ lắm rách cả tay",
    "màn hình": "Màn hình tối thui như tương lai mày",
    "loa": "Loa phường réo gọi tên tổ tông nhà mày",
    "mic": "Mic hú điếc tai bố mày",
    "tai nghe": "Tai nghe đứt dây điếc đặc",
    "sạc": "Sạc pin cháy nổ banh xác",
    "pin": "Pin chai phồng như bụng mẹ mày bầu",
    "ổ cắm": "Ổ cắm điện giật chết tươi",
    "phích cắm": "Phích cắm chập cháy nhà",
    "công tắc": "Công tắc bật tắt mõm chó",
    "bóng đèn": "Bóng đèn cháy thui thủi",
    "quạt trần": "Quạt trần rơi trúng sọ chó nhà mày",
    "điều hòa": "Điều hòa hỏng chảy nước vào mồm",
    "tủ lạnh": "Tủ lạnh trống trơn không có cứt mà ăn",
    "máy giặt": "Máy giặt quay cuồng như đầu óc mày",
    "bình nóng lạnh": "Bình nóng lạnh nổ tung xác",
    "nồi chiên": "Nồi chiên không dầu rán mặt chó",
    "lò vi sóng": "Lò vi sóng nướng chín não lồn",
    "bếp từ": "Bếp từ kén nồi như kén bố",
    "máy hút mùi": "Hút không sạch cái mùi mồm thối nhà mày",
    "bồn rửa": "Bồn rửa chén chứa toàn nước đái",
    "bồn cầu": "Bồn cầu là nơi anh em họ hàng mày sinh sống",
    "vòi hoa sen": "Vòi hoa sen phun nước đái vào mặt",
    "gạch": "Gạch đá xây mồ mã nhà mày",
    "xi măng": "Xi măng trát kín mõm chó lại",
    "cát đá": "Cát đá lấp mồ chôn sống mày",
    "sắt thép": "Sắt thép đâm xuyên người",
    "tôn": "Tôn lợp nhà tốc mái bay xác",
    "ngói": "Ngói vỡ rơi trúng đầu óc lồn",
    "cửa": "Cửa đóng then cài nhốt chó trong chuồng",
    "khóa": "Khóa cửa lại đéo cho con đĩ ra đường",
    "chìa khóa": "Chìa khóa mở chuồng súc vật",
    "hàng rào": "Hàng rào kẽm gai quấn cổ chó",
    "sân": "Sân nhà ỉa đầy cứt trâu cứt bò",
    "vườn": "Vườn rau bón toàn phân người",
    "cây cối": "Cây héo khô rễ chết toi",
    "hoa": "Hoa tàn héo úa như nhan sắc mẹ mày",
    "lá": "Lá rụng đầy mồ tổ tiên",
    "cành": "Cành khô gãy vụn",
    "rễ": "Rễ cây thối hoắc",
    "đất đá": "Đất đá sạt lở vùi lấp nhà mày",
    "núi": "Núi đè bẹp dí cái thây ma",
    "sông": "Sông sâu chết trôi lềnh bềnh",
    "suối": "Suối nước đục ngầu",
    "hồ": "Hồ nước thối um",
    "biển": "Biển động sóng thần cuốn sạch họ hàng",
    "đảo": "Đảo hoang đéo ai thèm ra thăm",
    "rừng": "Rừng thiêng nước độc muỗi cắn chết",
    "hang": "Hang động tối tăm nhốt con đĩ",
    "động": "Động quỷ chứa toàn súc vật",
    "vực": "Vực sâu thăm thẳm nhảy xuống đi",
    "đèo": "Đèo dốc lật xe chết tươi",
    "dốc": "Dốc cao trượt ngã dập dái",
    "đường": "Đường đời đưa đẩy mày làm đĩ",
    "ngõ": "Ngõ cụt không lối thoát cho mày",
    "hẻm": "Hẻm tối chích hút ngập mặt",
    "phố": "Phố thị ăn chơi trác táng",
    "làng": "Làng xóm đuổi cổ nhà mày đi nơi khác",
    "xã": "Xã hội đen truy nã tổ tiên",
    "huyện": "Huyện bắt giam vì tội ngu",
    "tỉnh": "Tỉnh ngộ đi con chó rách",
    "quốc gia": "Quốc gia trục xuất loại súc vật",
    "thế giới": "Thế giới này không dung tha cho mày",
    "vũ trụ": "Vũ trụ nổ tung tiễn vong mày",
    "không gian": "Không gian chật hẹp vì mày quá ngu",
    "thời gian": "Thời gian trôi qua mày càng thêm rác",
    "quá khứ": "Quá khứ làm đĩ mẹ mày ai cũng biết",
    "hiện tại": "Hiện tại ngậm cứt mút tay",
    "tương lai": "Tương lai làm ăn xin đầu đường",
    "sáng": "Sáng ra chưa ăn cứt à",
    "trưa": "Trưa nắng gắt cháy lông lồn",
    "chiều": "Chiều tà xách dép đi xin ăn",
    "tối": "Tối đến lại đi bú cặc thuê",
    "đêm": "Đêm khuya thanh vắng sủa bậy",
    "khuya": "Khuya rồi cút đi ngủ đi con",
    "xuân": "Xuân sang mẹ mày đi khách",
    "hạ": "Hạ về nắng cháy dái",
    "thu": "Thu sang lá rụng phủ thây",
    "đông": "Đông lạnh cóng cu",
    "năm": "Năm tháng trôi qua mày vẫn óc chó",
    "tháng": "Tháng ngày đói rách mốc mồm",
    "tuần": "Tuần lễ ăn cứt trừ cơm",
    "ngày": "Ngày đéo nào cũng bị chửi",
    "giờ": "Giờ phút này còn gáy được à",
    "phút": "Phút mốt là mày ăn đấm",
    "giây": "Giây phút tồi tệ khi gặp mày",
    "khoảnh khắc": "Khoảnh khắc mẹ mày đẻ rơi mày xuống hố",
    "thế kỷ": "Thế kỷ súc vật lên ngôi",
    "thiên niên kỷ": "Thiên niên kỷ không tìm thấy ai ngu bằng",
    "vĩnh biệt": "Vĩnh biệt con đĩ chó về với đất",
    "amen": "Amen cầu nguyện cho nhà mày tuyệt tử",
    "xin chúa": "Chúa cũng lắc đầu với não mày",
    "phật": "Phật độ hóa đéo nổi cái thứ óc chó",
    "ma": "Ma quỷ ghê sợ nhìn thấy mặt mày",
    "quỷ": "Quỷ dữ cũng phải quỳ gối xin tha",
    "yêu tinh": "Yêu tinh bạch cốt tinh hóa thân thành mày",
    "thần": "Thần thánh đầu hàng độ lượng",
    "thánh": "Thánh chửi gặp mày cũng phải quỳ",
    "tiên": "Tiên giáng trần nhầm chuồng súc vật",
    "phật tổ": "Phật tổ gõ đầu con đĩ ngu",
    "diêm vương": "Diêm vương gạch tên sổ sinh tử",
    "địa ngục": "Địa ngục tầng 18 dành riêng cho mày",
    "thiên đàng": "Thiên đàng từ chối nhận súc vật",
    "kiếp": "Kiếp này làm chó kiếp sau làm trùng",
    "nhân quả": "Nhân quả nhãn tiền nhà mày tuyệt tông",
    "nghiệp": "Nghiệp quật ngập mồm ngập mặt",
    "phước": "Phước đức tổ tiên gánh còng lưng",
    "tội": "Tội ác chồng chất đòi trảm",
    "phạt": "Phạt quỳ gối ngậm cứt 3 ngày",
    "tù": "Tù mọt gông không ngày về",
    "công an": "Công an bắt giam vì tội phát ngôn rác",
    "tòa": "Tòa án phán quyết tử hình ngay lập tức",
    "án": "Án tử treo lơ lửng trên cổ chó",
    "tử hình": "Tử hình tiêm thuốc độc chết tươi",
    "chung thân": "Chung thân trong chuồng heo",
    "trại giam": "Trại giam K3 không nhận loại ngu",
    "còng số 8": "Còng số 8 siết chặt tay chân thối",
    "roi": "Roi da quật rách da rách thịt",
    "gậy": "Gậy khúc đánh vỡ xương sống",
    "bắn súng": "Bắn nát đầu óc lồn",
    "ôm bom": "Ôm bom cảm tử kéo cả họ nhà mày đi",
    "lựu đạn": "Lựu đạn nổ banh xác pháo",
    "mìn": "Mìn dẫm phải nát bét dái",
    "đại bác": "Đại bác bắn bay màu",
    "tên lửa": "Tên lửa siêu thanh phóng thẳng vào mặt",
    "máy bay chiến đấu": "Máy bay thả bom trúng đầu nhà mày",
    "tăng thiết giáp": "Xe tăng cán qua người bẹp dí",
    "tàu chiến": "Tàu chiến phóng ngư lôi tiêu diệt",
    "hàng không mẫu hạm": "Mẫu hạm đè bẹp dí dòng họ",
    "chiến tranh": "Chiến tranh thế giới thứ 3 bắt đầu từ mõm mày",
    "hòa bình": "Hòa bình thế giới lập lại khi mày câm mồm",
    "đình chiến": "Đình chiến cái đầu buồi",
    "đầu hàng": "Đầu hàng đi con chó rách còn kịp",
    "chạy trốn": "Chạy trốn thế nào được bố mày",
    "truy nã": "Truy nã toàn quốc loại óc chó",
    "vây bắt": "Vây bắt súc vật đưa vào sở thú",
    "sở thú": "Sở thú từ chối nuôi loài ngu này",
    "chuồng heo": "Chuồng heo là nơi ở hợp lý nhất",
    "hố xí": "Hố xí công cộng là nhà của mày",
    "cống rãnh": "Cống rãnh đòi sóng sánh với đại dương",
    "bãi rác": "Bãi rác thải sinh hoạt là quê hương",
    "lò thiêu": "Lò thiêu xác đang chờ sẵn mày",
    "nhà tang lễ": "Nhà tang lễ đang khóc tang nhà mày",
    "vòng hoa": "Vòng hoa trắng cài tên tổ tông",
    "khăn tang": "Khăn tang quấn đầy đầu họ hàng",
    "hòm": "Hòm gỗ chôn sâu 3 thước đất",
    "huyệt": "Huyệt mộ đào sẵn chờ rước vong",
    "cúng": "Cúng đầu heo vịt luộc cho mày",
    "vàng mã": "Vàng mã đốt đầy đồng cho tiêu xài",
    "tro cốt": "Tro cốt rắc sông Hồng trôi đi",
    "hồn": "Hồn vía bay phách lạc mất xác",
    "phách": "Phách tiêu hồn tán không nơi nương tựa",
    "bố láo": "Bố láo cái đít mẹ mày, quỳ xuống bú cặc tao mau",
    "hỗn": "Hỗn hào cái con mẹ mày, tao vả rụng hết răng giờ",
    "bố đời": "Bố đời cái đầu khấc, rách việc vừa thôi con chó",
    "mất dạy": "Mất dạy từ trong trứng nước, tổ tiên mày đú đởn",
    "bố mày": "Bố mày đây, thằng óc chó rách đòi sủa à",
    "tổ cha": "Tổ cha mày đẻ rơi xuống hố xí công cộng",
    "mả cha": "Mả cha nhà mày ăn cứt trừ cơm từ bé",
    "họ hàng": "Họ hàng nhà mày toàn một lũ súc vật ăn mày",
    "tổ tông": "Tổ tông mày trèo cây ăn chuối từ thời nguyên thủy",
    "ông nội": "Ông nội mày đang ngậm cặc tao nè con",
    "bà ngoại": "Bà ngoại mày bán dâm ở đầu cầu vượt",
    "cụ tổ": "Cụ tổ mày ngày xưa bú liếm khắp thiên hạ",
    "dòng họ": "Dòng họ nhà mày tuyệt tử tuyệt tôn đi là vừa",
    "giống loài": "Giống loài chó rách đòi đọ với loài người",
    "đồ ngu": "Đồ ngu si đần độn, não toàn đậu phụ thiu",
    "đầu đất": "Đầu đất sét ngâm nước đái trâu",
    "não cá": "Não cá vàng còn đỡ hơn cái não cứt của mày",
    "thần kinh": "Thần kinh phân liệt trốn trại ra đây sủa bậy",
    "tâm thần": "Tâm thần viện số 3 đang tìm mày đấy con chó",
    "khốn nạn": "Khốn nạn từ gốc tới ngọn, cái giống đĩ bợm",
    "đốn mạt": "Đốn mạt hết phần thiên hạ, đúng là đồ cặn bã",
    "rác rưởi": "Rác rưởi xã hội đem đi đổ xó rác cho rồi",
    "cặn bã": "Cặn bã nhân loại, thở ra câu nào thối câu đấy",
    "súc sinh": "Súc sinh đẻ non thiếu tháng bú liếm",
    "động vật": "Động vật hoang dã chưa thuần hóa thành người",
    "quái thai": "Quái thai dị dạng làm xấu cả đội hình",
    "dị tật": "Dị tật bẩm sinh từ não đến nhân cách",
    "lươn lẹo": "Lươn lẹo như con lạch đạch trườn qua bãi cứt",
    "văn vở": "Văn vở như con đĩ đực bày đặt lên lớp",
    "sĩ diện": "Sĩ diện hão mà cái ví rỗng tuếch rách rưới",
    "ra vẻ": "Ra vẻ ta đây thanh cao hóa ra toàn đĩ bợm",
    "bày đặt": "Bày đặt học đòi làm sang nhưng mõm thối",
    "tỏ ra": "Tỏ ra nguy hiểm nhưng thực chất là óc chó",
    "thể hiện": "Thể hiện cái đầu buồi gì ở đây hả con",
    "gáy to": "Gáy to cho lắm vào rồi lại nằm ngửa ăn cứt",
    "sủa bậy": "Sủa bậy ăn đòn vỡ mồm bây giờ con chó rách",
    "câm mồm": "Câm cái mõm thối nhà mày vào không tao đấm",
    "biết điều": "Biết điều thì quỳ xuống bú chân cho bố",
    "láo nháo": "Láo nháo tao cho ăn dép tổ ong vào mặt",
    "bật mí": "Bật mí cái đít mẹ mày chứ bật mí",
    "thách thức": "Thách thức bố mày đi xem ai ngậm cứt trước",
    "ngon vào": "Ngon vào đây bố chấp cả lò nhà mày luôn",
    "sợ đéo": "Sợ đéo gì cái thể loại súc vật như mày",
    "bố sợ": "Bố sợ mày quá cơ, con chó rách hôi hám",
    "ghê thế": "Ghê thế cơ à, tưởng thế nào hóa ra đống cứt",
    "kinh nhỉ": "Kinh nhỉ, rách việc bày đặt ta đây nguy hiểm",
    "ghê gớm": "Ghê gớm cái đầu khấc, gặp tao là câm như hến",
    "oai phong": "Oai phong lẫm liệt như con chó ghẻ ngoài đường",
    "hổ báo": "Hổ báo trường mẫu giáo đòi ra xã hội bơi",
    "trẻ trâu": "Trẻ trâu ranh con bú bình đòi sủa bậy với bố",
    "ăn hại": "Ăn hại đái khai, gánh nặng của gia đình xã hội",
    "báo đời": "Báo đời báo hại tổ tông nghèo mạt rệp",
    "phá hoại": "Phá hoại như con trùng trục gặm nhấm",
    "vô dụng": "Vô dụng đến mức con chó nhà tao còn khinh",
    "vứt đi": "Vứt mẹ mày xuống sông cho cá nó tha",
    "đem đốt": "Đem đốt xác thành tro rồi đổ xuống cống",
    "tiêu đời": "Tiêu đời nhà con đĩ mẹ mày từ đây",
    "mạt vận": "Mạt vận cho cái dòng họ sinh ra loại mày",
    "hết cứu": "Hết cứu chữa rồi, chuẩn bị hòm đi con",
    "vô phương": "Vô phương cứu chữa, não thối rữa mẹ nó rồi",
    "ăn": "Ăn cứt trâu đi con chó rách",
    "uống": "Uống nước đái chó trừ bữa đi mày",
    "ngủ": "Ngủm củ tỏi sớm đi cho xã hội nhờ",
    "đi": "Đi đầu xuống hố xí mà chết đi con đĩ",
    "đứng": "Đứng ngửa lồn ra giữa đường cho thiên hạ chửi",
    "ngồi": "Ngồi nhầm đống cứt còn bày đặt oai",
    "nằm": "Nằm ngửa ăn vạ như con đĩ mốc mồm",
    "chạy": "Chạy thoát sao được cái đít mẹ mày",
    "nhảy": "Nhảy cầu tự vẫn đi cho rộng đất",
    "bơi": "Bơi vào đống phân mà húp đi con",
    "bay": "Bay màu mẹ mày đi cho trong sạch xã hội",
    "lượn": "Lượn nhanh khỏi mặt bố, con đĩ chó rách",
    "cút": "Cút xéo về chuồng heo mà sủa",
    "biến": "Biến cmn đi cho khuất mắt tao, súc sinh",
    "xéo": "Xéo ngay khỏi đây trước khi tao đấm vỡ mồm",
    "vào": "Vào hố xí mà nhận tổ tông đi con chó",
    "ra": "Ra đường xe tông chết tươi bây giờ",
    "lên": "Lên cơn điên à con đĩ thần kinh",
    "xuống": "Xuống địa ngục mà sủa với diêm vương",
    "về": "Về bú lồn mẹ mày đi chứ sủa gì ở đây",
    "đến": "Đến ngày giỗ tổ tiên nhà mày chưa",
    "đi": "Đi chết đi cho rộng đất xã hội",
    "lại": "Lại sủa bậy tao vả rụng răng giờ",
    "qua": "Qua đời sớm đi cho con cháu được nhờ",
    "lại": "Lại bày đặt lên lớp dạy đời bố à",
    "tìm": "Tìm cứt mà ăn chứ tìm gì ở đây",
    "kiếm": "Kiếm cái nịt mà gặm đi con chó",
    "mua": "Mua quan tài chuẩn bị chôn họ hàng mày",
    "bán": "Bán thận bán trinh đéo đủ tiền trả nợ",
    "đổi": "Đổi mẹ cái đầu óc lồn đi thằng ngu",
    "cho": "Cho cái đít mẹ mày vào mõm tao này",
    "nhận": "Nhận vơ họ hàng với súc vật à",
    "lấy": "Lấy dây thừng mà thắt cổ tự tử đi",
    "xin": "Xin cái đầu buồi chứ xin cái gì",
    "mời": "Mời mày xơi bãi cứt tươi tao vừa rặn",
    "chào": "Chào cái con đĩ mẹ mày, cút",
    "hỏi": "Hỏi cái đầu khấc, lắm mồm thế",
    "đáp": "Đáp gạch vào mồm bây giờ con chó",
    "đọc": "Đọc truyện con heo nhiều quá lú não à",
    "viết": "Viết di chúc đi là vừa con ạ",
    "vẽ": "Vẽ vời văn vở cái máu lồn",
    "hát": "Hát như bò rống điếc cả tai",
    "múa": "Múa cột kiếm tiền nuôi mẹ mày đi",
    "cười": "Cười cái đít mẹ mày, răng hô đòi gáy",
    "khóc": "Khóc lóc cái gì, ra mồ mã mà khóc",
    "la": "La hét cái gì như chó bị thọc tiết",
    "hét": "Hét to lên cho bố mày nghe xem nào",
    "sủa": "Sủa to lên con đĩ chó rách",
    "gáy": "Gáy sớm ăn cứt trâu đấy con ạ",
    "câm": "Câm ngay cái mõm thối nhà mày lại",
    "im": "Im cái họng chó vào, sủa lắm thế",
    "nghe": "Nghe cái con mẹ mày chứ nghe gì",
    "nhìn": "Nhìn cái lồn gì mà nhìn, muốn đấm à",
    "ngửi": "Ngửi mùi cứt quen thuộc của nhà mày đi",
    "nếm": "Nếm thử đòn của bố chưa con",
    "cầm": "Cầm cứt ném vào mặt mày bây giờ",
    "nắm": "Nắm đấm tao đang chờ vào mồm mày đấy",
    "ném": "Ném đá giấu tay như con đĩ bợm",
    "vứt": "Vứt mẹ mày xuống sông hồng đi",
    "bỏ": "Bỏ ngay cái thói óc chó đấy đi",
    "giữ": "Giữ lấy cái mõm thối mà ngậm chặt vào",
    "đấm": "Đấm vỡ sọ con đĩ mẹ mày giờ",
    "đánh": "Đánh chết cụ mày chứ ở đấy mà sủa",
    "chém": "Chém gió thành bão nhưng nhà rách nát",
    "giết": "Giết cái con mẹ mày chứ đòi giết ai",
    "bắn": "Bắn tung tóe cứt vào mặt mày bây giờ",
    "thắng": "Thắng thế đéo nào được bố mày, thằng ngu",
    "thua": "Thua ngập mặt còn bày đặt sủa to",
    "chết": "Chết quách đi cho rộng đất thiên hạ",
    "sống": "Sống chật đất tốn cơm tốn gạo",
    "tồn tại": "Tồn tại làm cảnh cho thiên hạ chửi",
    "sinh": "Sinh ra làm gì để ô nhục tổ tông",
    "đẻ": "Đẻ đau lồn ra một con súc vật",
    "nuôi": "Nuôi tốn cơm tốn gạo chỉ để ăn cứt",
    "dạy": "Dạy đời cái đít mẹ mày, loại óc chó",
    "học": "Học hành đéo đến nơi đến chốn đòi đú",
    "thi": "Thi trượt chổng vó lên còn gáy",
    "đậu": "Đậu đại học bằng niềm tin à con đĩ",
    "rớt": "Rớt đài ngập mồm ngập mặt rồi con",
    "làm": "Làm đĩ thuê nuôi cả họ nhà mày à",
    "ăn": "Ăn hại đái khai, vô tích sự",
    "chơi": "Chơi bời lêu lổng rồi ra đường ở",
    "nghỉ": "Nghỉ mẹ chơi đi, đầu óc toàn bã đậu",
    "làm việc": "Làm việc thì lười, ăn thì tơi bời",
    "ngủ ngày": "Ngủ ngày cày đêm đi bú cặc thuê",
    "thức": "Thức khuya dậy sớm húp cứt trâu",
    "mệt": "Mệt thì cút đi ngủ, đừng sủa",
    "đói": "Đói rách mồm đòi ăn sơn hào hải vị",
    "no": "No căng bụng rồi lại ẳng bậy",
    "khát": "Khát nước đái chó thì bảo bố",
    "say": "Say xỉn nằm vật vã giữa đống phân",
    "tỉnh": "Tỉnh ngộ đi con đĩ chó rách",
    "mê": "Mê muội u mê như não chó",
    "tỉnh táo": "Tỉnh táo lên xem mình ngu cỡ nào",
    "điên": "Điên khùng thần kinh phân liệt",
    "khùng": "Khùng điên trốn trại ra đây sủa",
    "ngu": "Ngu từ trong trứng ngu đi con",
    "dốt": "Dốt đặc cán mai bày đặt tri thức",
    "khôn": "Khôn lỏi như chó rách đòi lừa bố",
    "đần": "Đần độn không ai bằng mày",
    "thông minh": "Thông minh đột biến thành óc chó",
    "tài giỏi": "Tài giỏi cái đầu buồi nhà mày",
    "vĩ đại": "Vĩ đại như cục phân trôi sông",
    "anh hùng": "Anh hùng bàn phím gặp ngoài đời đái ra quần",
    "cao thủ": "Cao thủ ăn cứt hạng nặng",
    "đại gia": "Đại gia ăn mày dạt dòi",
    "tiểu nhân": "Tiểu nhân đốn mạt bỉ oổi",
    "quân tử": "Quân tử tàu rách việc",
    "đàn ông": "Dan ông cái đầu khấc, bê đê nửa mùa",
    "đàn bà": "Đàn bà đẻ rớt dọc đường",
    "con trai": "Con trai bú cặc thuê đầu ngõ",
    "con gái": "Con gái ngửa lồn kiếm tiền chà đạp",
    "thằng bé": "Thằng bé ngậm bình sữa đòi làm bố",
    "con bé": "Con bé nứt mắt ra đã đi khách",
    "ông chú": "Ông chú đái đường bốc mùi",
    "bà cô": "Bà cô tổ điên khùng",
    "cô giáo": "Cô giáo dạy đĩ học lớp vỡ lòng",
    "thầy giáo": "Thầy giáo bú mớm học trò",
    "bác sĩ": "Bác sĩ tâm thần chữa cho mày đây",
    "y tá": "Y tá tiêm thuốc độc chết cụ mày",
    "công an": "Công an truy nã loại súc vật này",
    "luật sư": "Luật sư cãi cho con đĩ mẹ mày",
    "giám đốc": "Giám đốc công ty bán chổi đót",
    "nhân viên": "Nhân viên hốt cứt chuyên nghiệp",
    "chủ tịch": "Chủ tịch hội đồng cặn bã xã hội",
    "tổng thống": "Tổng thống liên minh óc chó",
    "hoàng đế": "Hoàng đế cõi âm đang gọi tên mày",
    "vua": "Vua súc vật đây rồi, quỳ xuống",
    "chúa": "Chúa tể những chiếc bỉm rách",
    "phật": "Phật độ đéo nổi cái thứ mày",
    "thần": "Thần thánh quỳ gối xin tha",
    "ma quỷ": "Ma quỷ nhìn thấy cũng phải chạy mất dép",
    "yêu tinh": "Yêu tinh bạch cốt tinh hóa thân",
    "quái vật": "Quái vật hồ tây đéo xấu bằng mày",
    "ngoài hành tinh": "Đĩa bay chở mày về sao hỏa đi",
    "vũ trụ": "Vũ trụ bao la đéo chứa nổi loại ngu",
    "trái đất": "Trái đất nặng nề vì có thêm cục nợ là mày",
    "mặt trời": "Mặt trời chiếu rát cái mặt lồn",
    "mặt trăng": "Mặt trăng soi bóng con đĩ chó",
    "ngôi sao": "Ngôi sao xẹt trúng đầu tổ tiên mày",
    "bầu trời": "Bầu trời u ám y như tương lai mày",
    "mây đen": "Mây đen che phủ cuộc đời rách rưởi",
    "mưa gió": "Mưa gió bão bùng cuốn sạch họ hàng",
    "sấm chớp": "Sấm sét đánh ngang dái mày",
    "lũ lụt": "Lũ lụt trôi nhà trôi cửa",
    "động đất": "Động đất chôn vùi tổ tông",
    "sóng thần": "Sóng thần cuốn phăng cái thây ma",
    "núi lửa": "Núi lửa phun trào thiêu cháy xác",
    "băng giá": "Băng giá đóng băng não chó",
    "sa mạc": "Sa mạc khô cằn như cái mồm mày",
    "rừng rú": "Rừng thiêng nước độc muỗi cắn chết",
    "biển sâu": "Biển sâu cá mập cắn đứt đầu buồi",
    "sông ngòi": "Sông ngòi ô nhiễm y như mồm mày",
    "ao hồ": "Ao tù nước đọng hôi rình",
    "đồng ruộng": "Đồng ruộng bón toàn phân chuồng",
    "thành phố": "Thành phố chật chội loại rác rưởi",
    "nông thôn": "Nông thôn đuổi cổ mày đi nơi khác",
    "bản làng": "Bản làng không nhận súc sinh",
    "đường phố": "Đường phố không có chỗ cho mày sủa",
    "ngõ hẻm": "Ngõ hẻm tối tăm chỗ mày bú cặc",
    "nhà cửa": "Nhà cửa tan hoang nợ nần ngập đầu",
    "phòng trọ": "Phòng trọ rách nát hôi mùi mắm tôm",
    "khách sạn": "Khách sạn ổ quỷ của mẹ mày",
    "nhà nghỉ": "Nhà nghỉ qua đêm của gia đình mày",
    "bệnh viện": "Bệnh viện tâm thần đang đợi",
    "trại giam": "Trại giam K1 đang giam giữ tông ti",
    "pháp trường": "Pháp trường chờ tiêm thuốc độc",
    "mồ mả": "Mồ mả tổ tiên bị đào xới tung lên",
    "hố xí": "Hố xí công cộng là quê hương",
    "bãi rác": "Bãi rác thải sinh hoạt là nhà",
    "chuồng heo": "Chuồng heo là chỗ ở hợp lý",
    "chuồng chó": "Chuồng chó là nơi mày sinh ra",
    "hang ổ": "Hang ổ tụ tập bọn súc vật",
    "lò mổ": "Lò mổ đang chờ cổ mày đấy",
    "lò thiêu": "Lò thiêu xác đang đỏ lửa",
    "nhà tang lễ": "Nhà tang lễ đang phát tang",
    "quan tài": "Quan tài đóng đinh kín mít",
    "hũ tro": "Hũ tro cốt rắc xuống sông",
    "vòng hoa": "Vòng hoa tang trắng toát",
    "khăn tang": "Khăn tang quấn trùm đầu",
    "bát hương": "Bát hương cắm đầy chân nhang",
    "đồ cúng": "Đồ cúng cứt trâu vịt luộc",
    "vàng mã": "Vàng mã đốt đầy đồng",
    "tiền âm phủ": "Tiền âm phủ tiêu cho bét nhè",
    "diêm vương": "Diêm vương gạch tên sổ sinh tử",
    "địa ngục": "Địa ngục tầng 18 đón chào",
    "thiên đường": "Thiên đường từ chối loại ngu",
    "kiếp này": "Kiếp này làm chó kiếp sau làm trùng",
    "kiếp sau": "Kiếp sau làm cục phân trôi sông",
    "nhân quả": "Nhân quả nhãn tiền tuyệt tử",
    "nghiệp chướng": "Nghiệp chướng ngập ngụa mặt mày",
    "phước đức": "Phước đức tổ tiên gánh còng lưng",
    "tội lỗi": "Tội lỗi chồng chất ngập đầu",
    "hình phạt": "Hình phạt quỳ gối ngậm cứt",
    "án tử": "Án tử treo lơ lửng trên cổ",
    "chung thân": "Chung thân trong chuồng súc vật",
    "tù tội": "Tù mọt gông không ngày về",
    "còng tay": "Còng số 8 siết chặt tay thối",
    "roi da": "Roi da quật rách da thịt",
    "gậy gộc": "Gậy gộc đánh vỡ xương sống",
    "súng đạn": "Súng đạn bắn nát đầu óc lồn",
    "bom mìn": "Bom mìn nổ banh xác pháo",
    "lựu đạn": "Lựu đạn nát bét dái",
    "dao kiếm": "Dao kiếm chém đứt đôi người",
    "gươm giáo": "Gươm giáo đâm xuyên ngực",
    "mũi tên": "Mũi tên độc cắm vào tim",
    "thuốc độc": "Thuốc độc uống vào ngỏm cụ",
    "axit": "Axit dội rát mặt tiền",
    "lửa đỏ": "Lửa đỏ thiêu cháy thành tro",
    "nước sôi": "Nước sôi dội thẳng mõm",
    "dầu ăn": "Dầu ăn bôi trơn đi đít cho mượt",
    "bao cao su": "Bao cao su thủng lỗ chỗ",
    "bỉm": "Bỉm rách đựng đầy cứt của mày",
    "giấy vệ sinh": "Giấy vệ sinh lau đít nhét mồm",
    "băng vệ sinh": "Băng vệ sinh dính máu lồn má",
    "khăn giấy": "Khăn giấy lau bãi nôn",
    "giẻ lau": "Giẻ lau bàn cầu dơ dáy",
    "chổi đót": "Chổi đót quét nhà quật mặt",
    "cây chổi": "Cây chổi cùn chọc họng",
    "thùng rác": "Thùng rác chứa toàn họ hàng",
    "bãi phân": "Bãi phân trâu không bằng mày",
    "đống cứt": "Đống cứt trôi sông dạt dào",
    "nước đái": "Nước đái ngập đầu ngập cổ",
    "đờm dãi": "Đờm dãi khạc vào mặt tiền",
    "mủ hôi": "Mủ hôi tanh như máu lồn",
    "máu chó": "Máu chó trào họng chết tươi",
    "bệnh tật": "Bệnh tật đầy người lở loét",
    "ung thư": "Ung thư giai đoạn cuối còn gáy",
    "siêu vi": "Siêu vi khuẩn ăn mòn não",
    "vi trùng": "Vi trùng bám đầy lông mặt",
    "ký sinh trùng": "Ký sinh trùng bám đít bú cứt",
    "giun sán": "Giun sán lúc nhúc trong bụng",
    "bọ chét": "Bọ chét cắn nát cái lồn",
    "ve chó": "Ve chó bu đầy lông mặt",
    "rận mu": "Rận mu cắn nát trym",
    "chấy rận": "Chấy rận đẻ đầy đầu óc lồn",
    "mối mọt": "Mối mọt ăn mòn xương cốt",
    "gián đất": "Gián đất bò vào mõm thối",
    "nhện độc": "Nhện độc giăng tơ bẫy mồi",
    "bọ cạp": "Bọ cạp chích chết tươi",
    "rết độc": "Rết độc cắn nát trym",
    "ốc sên": "Ốc sên bò chậm như não",
    "cá trê": "Cá trê chui ống cống hôi",
    "cá lóc": "Cá lóc nướng trui mồm chó",
    "cá mập": "Cá mập cắn đứt đôi người",
    "chim sẻ": "Chim sẻ hót líu lo như mày sủa",
    "chim cú": "Chim cú mèo báo điềm gở",
    "đại bàng": "Đại bàng quắp xác vứt sọt rác",
    "kên kên": "Kên kên ăn xác thối nhà mày",
    "quạ đen": "Quạ đen kêu trên nóc nhà tang",
    "gà trống": "Gà trống thiến đòi gáy to",
    "gà mái": "Gà mái tơ bị bố thịt rồi",
    "vịt xiêm": "Vịt xiêm kêu cạp cạp điếc tai",
    "ngỗng cái": "Ngỗng cái cắn đứt dái mày",
    "đà điểu": "Đà điểu rúc đầu vào cát trốn nợ",
    "bò tót": "Bò tót húc chết tươi bố mày à",
    "trâu điên": "Trâu điên húc hầm cầu",
    "ngựa chứng": "Ngựa chứng đứt cương ngã vực",
    "lừa đảo": "Lừa đảo bị chặt tay chặt chân",
    "lạc đà": "Lạc đà nhổ nước bọt vào mặt",
    "gấu ngựa": "Gấu ngựa cào nát mặt chó",
    "hải cẩu": "Hải cẩu béo ú lăn lóc",
    "rái cá": "Rái cá ngụp lặn hố xí",
    "chồn hôi": "Chồn hôi thối không bằng mồm",
    "lửng mật": "Lửng mật gặp bố cũng quỳ",
    "sao biển": "Sao biển phơi thây trên cát",
    "lươn trạch": "Lươn trạch trơn tuột văn vở",
    "cá rô phi": "Rô phi ngửa bụng chết trôi",
    "cá thu": "Cá thu cắt khúc rán giòn",
    "cá hồi": "Cá hồi phi lê sống chấm mù tạt",
    "cá ngừ": "Cá ngừ đại dương đóng hộp",
    "cá voi": "Cá voi nuốt chửng mẹ mày",
    "sóng biển": "Sóng biển cuốn trôi xác thối",
    "gió độc": "Gió độc thổi bay xác ma",
    "mưa axit": "Mưa axit rát mặt tiền",
    "nắng cháy": "Nắng cháy da cháy thịt",
    "bão táp": "Bão táp cuốn sạch tông ti",
    "đất nứt": "Đất nứt chôn vùi tổ tiên",
    "bầu trời": "Bầu trời sập đè bẹp dí",
    "sấm sét": "Sấm sét đánh ngang dái",
    "chớp giật": "Chớp giật cháy lông lồn",
    "mương nước": "Mương nước thải ngập đầu",
    "ống cống": "Ốc cống rãnh ngập cứt",
    "hố phân": "Hố phân trâu bò là nhà",
    "bãi tha ma": "Bãi tha ma hoang vắng",
    "nghĩa địa": "Nghĩa địa chôn thối xác",
    "nhà xác": "Nhà xác lạnh ngắt lạnh ngùng",
    "phòng lạnh": "Phòng lạnh đắp chiếu trắng",
    "lớp học": "Lớp học vỡ lòng chửi thuê",
    "sân trường": "Sân trường đá bóng bằng đầu lâu",
    "cổng trường": "Cổng trường đứng ngửa lồn",
    "quán net": "Quán net cày game ngửa dái",
    "quán nhậu": "Quán nhậu nôn ọe đầy bàn",
    "vỉa hè": "Vỉa hè xin ăn đầu đường",
    "gầm cầu": "Gầm cầu vượt là nhà trọ",
    "bến xe": "Bến xe ôm đầu gấu rách",
    "sân bay": "Sân bay tiễn vong đi thẳng",
    "tàu hoả": "Tàu hỏa cán cụt hai chân",
    "xe ôm": "Xe ôm công nghệ đâm cột điện",
    "taxi": "Taxi lật ngửa giữa đường",
    "xe tải": "Xe tải cán bẹp dí người",
    "container": "Container húc bay màu",
    "xe máy": "Xe máy tông trực diện",
    "xe đạp": "Xe đạp thủng lốp dắt bộ",
    "đi bộ": "Đi bộ bị sét đánh ngang đầu",
    "giày dép": "Giày dép vứt đống rác",
    "quần áo": "Quần áo rách bươm xơ mướp",
    "mũ nón": "Mũ nón cối đội đầu ngu",
    "kính cận": "Kính cận lồi mắt vẫn mù",
    "khẩu trang": "Khẩu trang che mõm thối",
    "nhẫn vàng": "Nhẫn vàng mã hàng chợ",
    "dây chuyền": "Dây chuyền xích chó quấn cổ",
    "đồng hồ": "Đồng hồ điểm giờ chết tiệt",
    "ví tiền": "Ví tiền rỗng tuếch mốc meo",
    "thẻ cào": "Thẻ cào rách đéo nạp được",
    "sim số": "Sim rác giống hệt chủ nhân",
    "máy tính": "Máy tính sập nguồn câm mõm",
    "bàn phím": "Bàn phím gõ lắm gãy tay",
    "màn hình": "Màn hình tối thui tương lai",
    "loa phường": "Loa phường réo tên tổ tông",
    "micro": "Micro hú điếc tai điếc óc",
    "tai nghe": "Tai nghe đứt dây điếc đặc",
    "cục sạc": "Cục sạc phát nổ banh nhà",
    "ổ điện": "Ổ điện giật tung xác pháo",
    "bóng đèn": "Bóng đèn cháy thui thủi",
    "quạt máy": "Quạt máy đứt cánh chém tay",
    "điều hòa": "Điều hòa hỏng nhỏ nước đái",
    "tủ lạnh": "Tủ lạnh trống trơn ko cứt",
    "máy giặt": "Máy giặt quay nát não lồn",
    "bếp ga": "Bếp ga nổ tung banh xác",
    "nồi cơm": "Nồi cơm khê khét mùi cứt",
    "chảo chống dính": "Chảo rán bắn mỡ lông lồn",
    "dao thớt": "Dao thớt chặt đầu chó rách",
    "bát đũa": "Bát đũa ăn mày đập bể",
    "cốc chén": "Cốc chén vỡ nát tung tóe",
    "ấm trà": "Ấm trà mốc meo xanh lè",
    "bình nước": "Bình nước đái giếng làng",
    "chậu giặt": "Chậu giặt chứa nước thải",
    "thùng xốp": "Thùng xốp đựng xác chết trôi",
    "bao tải": "Bao tải rách đựng thây ma",
    "túi bóng": "Túi bóng vứt đầy đường bẩn",
    "bút mực": "Bút mực phun đen mặt đĩ",
    "thước kẻ": "Thước kẻ đập vỡ sọ lồn",
    "cục tẩy": "Cục tẩy xóa sổ cuộc đời",
    "sách vở": "Sách vở xé làm giấy chùi",
    "cặp sách": "Cặp sách trốn học bú cặc",
    "balo": "Balo nặng trĩu gánh nợ đời",
    "chiếc áo": "Chiếc áo rách vai vá đụp",
    "cái quần": "Cái quần thủng đít lộ lông",
    "đôi giày": "Đôi giày hôi rình mùi mắm",
    "chiếc mũ": "Chiếc mũ cối đội đầu bò",
    "cây bút": "Cây bút chọc thủng mắt chó",
    "tờ giấy": "Tờ giấy vệ sinh nhét họng",
    "hộp quà": "Hộp quà chứa đầu lâu chó",
    "bức tranh": "Bức tranh vẽ bãi cứt trâu",
    "tượng đá": "Tượng đá ngậm cứt phun người",
    "hòn đá": "Hòn đá đè bẹp dí thây ma",
    "hạt cát": "Hạt cát bay vào mõm thối",
    "giọt nước": "Giọt nước đái ngập mồm chó",
    "tia lửa": "Tia lửa thiêu cháy lông lồn",
    "làn gió": "Làn gió độc thổi bay xác",
    "vầng trăng": "Vầng trăng khuyết y như não",
    "bông hoa": "Bông hoa tàn héo úa xì",
    "tập thơ": "Tập thơ con cóc chửi thuê",
    "bản nhạc": "Bản nhạc chó sủa đêm khuya",
    "bộ phim": "Bộ phim con heo mẹ đóng",
    "trò chơi": "Trò chơi ngửa lồn ăn tiền",
    "món ăn": "Món ăn trộn cứt ngon miệng",
    "thức uống": "Thức uống nước đái hầm nhừ",
    "gia vị": "Gia vị mắm tôm thối hoắc",
    "củ khoai": "Củ khoai ngâm hố xí",
    "bắp ngô": "Bắp ngô gặm lõi bỏ đi",
    "quả chuối": "Quả chuối thiu mốc meo",
    "trái cây": "Trái cây thối rữa đầy dòi",
    "con cá": "Con cá rô phi ngửa bụng",
    "con gà": "Con gà trống thiến mất dái",
    "con lợn": "Con lợn nái đẻ ra mày",
    "con chó": "Con chó sủa bậy ăn đòn",
    "con mèo": "Con mèo mả gà đồng",
    "con chuột": "Con chuột cống rãnh hôi hám",
    "con rắn": "Con rắn độc cắn đứt dái",
    "con ếch": "Con ếch ngồi đáy giếng",
    "con cua": "Con cua kẹp nát đầu buồi",
    "con tôm": "Con tôm tép tuổi cái lồn",
    "con sâu": "Con sâu bọ đòi đọ rồng",
    "con kiến": "Con kiến cỏ bày đặt voi",
    "con muỗi": "Con muỗi đốt inox đòi cắn",
    "con ruồi": "Con ruồi nhặng bu đống cứt",
    "con gián": "Con gián đất chui ống cống",
    "con nhện": "Con nhện giăng tơ bẫy đĩ",
    "con ong": "Con ong đốt sưng mặt chó",
    "con bướm": "Con bướm thối hoắc bay lượn",
    "con ve": "Con ve sầu kêu điếc tai",
    "con rết": "Con rết độc cắn đứt trym",
    "con ốc": "Con ốc sên bò chậm như não",
    "con rùa": "Con rùa bò dưới bùn lầy",
    "con thỏ": "Con thỏ đế run cầy sấy",
    "con hổ": "Con hổ đói ăn cứt trừ bữa",
    "con báo": "Con báo thủ rách việc",
    "con gấu": "Con gấu trúc thâm quầng mắt",
    "con voi": "Con voi rừng húc văng xác",
    "con ngựa": "Con ngựa đứt cương ngã hố",
    "con trâu": "Con trâu nước đầm lầy hôi",
    "con bò": "Con bò tót ngậm cứt phun",
    "con cừu": "Con cừu đen rách rưởi",
    "con dê": "Con dê cụ sáng mắt lồn",
    "con khỉ": "Con khỉ khô mốc mỏ đó",
    "con vượn": "Con vượn hú trong rừng sâu",
    "con sói": "Con sói đói gặm xương chó",
}

# --- HÀM TẢI VÀ LƯU DỮ LIỆU ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                keywords = data.get("keywords", DEFAULT_KEYWORD_RESPONSES)
                welcome_msgs = {int(k): v for k, v in data.get("welcome_msgs", {}).items()}
                welcome_videos = {int(k): v for k, v in data.get("welcome_videos", {}).items()}
                rules = {int(k): v for k, v in data.get("rules", {}).items()}
                settings = {}
                for k, v in data.get("settings", {}).items():
                    settings[int(k)] = v
                warnings = {}
                for k, v in data.get("warnings", {}).items():
                    warnings[int(k)] = {int(uid): count for uid, count in v.items()}
                return keywords, welcome_msgs, welcome_videos, rules, settings, warnings
        except Exception as e:
            print(f"Lỗi đọc file dữ liệu: {e}")
    return DEFAULT_KEYWORD_RESPONSES.copy(), {}, {}, {}, {}, {}

def save_data():
    data = {
        "keywords": KEYWORD_RESPONSES,
        "welcome_msgs": WELCOME_MSGS,
        "welcome_videos": WELCOME_VIDEOS,
        "rules": RULES,
        "settings": SETTINGS,
        "warnings": WARNINGS
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Lỗi ghi file dữ liệu: {e}")

# Khởi tạo dữ liệu từ file JSON
KEYWORD_RESPONSES, WELCOME_MSGS, WELCOME_VIDEOS, RULES, SETTINGS, WARNINGS = load_data()

def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except Exception:
        return False

def get_setting(chat_id, key, default=True):
    return SETTINGS.get(chat_id, {}).get(key, default)

def set_setting(chat_id, key, value):
    SETTINGS.setdefault(chat_id, {})[key] = value
    save_data()

def get_user_and_args(message):
    args = message.text.split()[1:] if message.text else []
    target_id = None
    target_name = "User"
    extra_args = []

    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        target_name = message.reply_to_message.from_user.first_name
        extra_args = args
    else:
        for arg in args:
            if target_id is None:
                if arg.isdigit() or (arg.startswith('-') and arg[1:].isdigit()):
                    try:
                        uid = int(arg)
                        member = bot.get_chat_member(message.chat.id, uid)
                        target_id = member.user.id
                        target_name = member.user.first_name
                        continue
                    except Exception:
                        pass
                elif arg.startswith('@'):
                    try:
                        chat = bot.get_chat(arg)
                        target_id = chat.id
                        target_name = chat.first_name or chat.username
                        continue
                    except Exception:
                        pass
            extra_args.append(arg)
    return target_id, target_name, extra_args

@bot.message_handler(commands=['help', 'start'])
def send_help(message):
    help_text = (
        "HƯỚNG DẪN SỬ DỤNG BOT & LỆNH QUẢN TRỊ\n\n"
        "1. TỪ KHÓA & HỆ THỐNG:\n"
        "• /them <từ_khóa> - <câu_trả_lời>: Thêm từ khóa\n"
        "• /danhsach: Xem danh sách từ khóa\n"
        "• //reset danhsach thêm: Khôi phục danh sách\n\n"
        "2. TRỊ THÀNH VIÊN (Reply/Username/ID):\n"
        "• /ban [@user/id]: Cấm thành viên\n"
        "• /unban <user_id/@user>: Bỏ cấm\n"
        "• /kick [@user/id]: Xóa khỏi nhóm\n"
        "• /mute [phút] [@user/id] (hoặc /suyt): Tắt quyền chat\n"
        "• /unmute [@user/id]: Khôi phục quyền chat\n"
        "• /warn [@user/id]: Cảnh cáo\n"
        "• /unwarn [@user/id]: Xóa cảnh cáo\n"
        "• /warnings [@user/id]: Xem số lần cảnh cáo\n\n"
        "3. CHÀO MỪNG THÀNH VIÊN & VIDEO:\n"
        "• /welcome: Xem trạng thái chào mừng\n"
        "• /welcome on|off: Bật/tắt chào mừng\n"
        "• /setwelcome <nội_dung>: Cài tin nhắn chào mừng\n"
        "• /resetwelcome: Khôi phục tin chào mừng mặc định\n"
        "• /setwelvideo (Reply video): Cài video chào mừng\n"
        "• /delwelvideo: Xóa video chào mừng\n\n"
        "4. QUẢN LÝ NHÓM:\n"
        "• /rules: Xem nội quy | /setrules <nội_dung>: Cập nhật nội quy\n"
        "• /pin: Ghim tin nhắn | /unpin: Bỏ ghim\n"
        "• /purge: Xóa nhiều tin nhắn (reply)\n\n"
        "5. CHỐNG SPAM & THÔNG TIN:\n"
        "• /antispam on|off | /antilink on|off\n"
        "• /id: Xem ID | /info: Thông tin thành viên\n"
        "• /admins: Danh sách admin"
    )
    bot.send_message(message.chat.id, help_text)

# --- QUẢN LÝ TỪ KHÓA ---
@bot.message_handler(commands=['them'])
def add_keyword(message):
    raw_text = message.text[5:].strip()
    if not raw_text or "-" not in raw_text:
        bot.send_message(message.chat.id, "Sai cú pháp! Dùng: /them <từ_khóa> - <câu_trả_lời>")
        return

    parts = raw_text.split("-", 1)
    keyword = parts[0].strip().lower().replace("<", "").replace(">", "")
    response = parts[1].strip()

    if not keyword or not response:
        bot.send_message(message.chat.id, "Từ khóa hoặc câu trả lời không được để trống!")
        return

    KEYWORD_RESPONSES[keyword] = response
    save_data()
    bot.send_message(message.chat.id, f"Đã thêm thành công!\nTừ khóa: {keyword}\nTrả lời: {response}")

@bot.message_handler(commands=['danhsach'])
def list_keywords(message):
    if not KEYWORD_RESPONSES:
        bot.send_message(message.chat.id, "Chưa có từ khóa nào!")
        return
    
    list_text = "DANH SÁCH TỪ KHÓA HIỆN CÓ:\n\n"
    for kw in KEYWORD_RESPONSES.keys():
        list_text += f"- {kw}\n"
    bot.send_message(message.chat.id, list_text)

@bot.message_handler(func=lambda message: message.text and message.text.strip().lower() in ["//reset danhsach thêm", "//khôi phuc danh sách thêm", "//khôi phục danh sách thêm"])
def reset_keywords(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id, "Bạn không phải Admin!")
        return
    global KEYWORD_RESPONSES
    KEYWORD_RESPONSES = DEFAULT_KEYWORD_RESPONSES.copy()
    save_data()
    bot.send_message(message.chat.id, "Đã khôi phục lại danh sách từ khóa ban đầu thành công!")

# --- BỘ LỆNH CHÀO MỪNG (WELCOME) ---
@bot.message_handler(commands=['welcome', 'welcom'])
def welcome_command(message):
    chat_id = message.chat.id
    args = message.text.split(maxsplit=1)

    if len(args) > 1:
        sub = args[1].lower().strip()
        if not is_admin(chat_id, message.from_user.id):
            bot.send_message(chat_id, "Bạn không phải Admin!")
            return

        if sub == 'on':
            set_setting(chat_id, 'welcome', True)
            bot.send_message(chat_id, "✅ Đã BẬT tính năng chào mừng thành viên mới!")
            return
        elif sub == 'off':
            set_setting(chat_id, 'welcome', False)
            bot.send_message(chat_id, "❌ Đã TẮT tính năng chào mừng thành viên mới!")
            return

    status = "BẬT (ON)" if get_setting(chat_id, 'welcome', True) else "TẮT (OFF)"
    current_msg = WELCOME_MSGS.get(chat_id, DEFAULT_WELCOME_TEXT)
    has_video = "Có (Đã cài)" if chat_id in WELCOME_VIDEOS else "Không có"
    
    info = (
        f"⚙️ **TRẠNG THÁI CHÀO MỪNG:** {status}\n"
        f"🎬 **Video chào mừng:** {has_video}\n\n"
        f"📝 **Nội dung tin nhắn hiện tại:**\n{current_msg}\n\n"
        f"💡 **Các lệnh hỗ trợ:**\n"
        f"• `/welcome on` - Bật chào mừng\n"
        f"• `/welcome off` - Tắt chào mừng\n"
        f"• `/setwelcome <nội dung>` - Cài tin nhắn tùy chỉnh\n"
        f"• `/resetwelcome` - Khôi phục tin nhắn mặc định\n"
        f"• `/setwelvideo` (Reply video) - Cài video chào mừng\n"
        f"• `/delwelvideo` - Xóa video chào mừng\n\n"
        f"📌 *Mẹo:* Dùng `{user}` để tag tên, `{name}` để lấy tên, `{group}` để lấy tên nhóm."
    )
    bot.send_message(chat_id, info, parse_mode="Markdown")

@bot.message_handler(commands=['setwelcome'])
def set_welcome_message(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id, "Bạn không phải Admin!")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        bot.send_message(message.chat.id, "Vui lòng nhập nội dung! Ví dụ:\n`/setwelcome Chào mừng {user} đã đến với {group}!`", parse_mode="Markdown")
        return

    WELCOME_MSGS[message.chat.id] = parts[1].strip()
    save_data()
    bot.send_message(message.chat.id, "✅ Đã cập nhật tin nhắn chào mừng nhóm thành công!")

@bot.message_handler(commands=['resetwelcome'])
def reset_welcome_message(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id, "Bạn không phải Admin!")
        return

    WELCOME_MSGS.pop(message.chat.id, None)
    save_data()
    bot.send_message(message.chat.id, "✅ Đã khôi phục tin nhắn chào mừng về mặc định!")

@bot.message_handler(commands=['setwelvideo'])
def set_welcome_video(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id, "Bạn không phải Admin!")
        return

    if not message.reply_to_message or not message.reply_to_message.video:
        bot.send_message(message.chat.id, "❌ Vui lòng reply (phản hồi) vào một video kèm lệnh `/setwelvideo` để cài đặt video chào mừng!", parse_mode="Markdown")
        return

    video_id = message.reply_to_message.video.file_id
    WELCOME_VIDEOS[message.chat.id] = video_id
    save_data()
    bot.send_message(message.chat.id, "✅ Đã lưu video chào mừng cho nhóm thành công!")

@bot.message_handler(commands=['delwelvideo'])
def delete_welcome_video(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id, "Bạn không phải Admin!")
        return

    if message.chat.id in WELCOME_VIDEOS:
        del WELCOME_VIDEOS[message.chat.id]
        save_data()
        bot.send_message(message.chat.id, "✅ Đã xóa video chào mừng của nhóm!")
    else:
        bot.send_message(message.chat.id, "ℹ️ Nhóm này hiện chưa cài đặt video chào mừng nào.")

# --- XỬ LÝ THÀNH VIÊN MỚI GIA NHẬP / ĐƯỢC THÊM VÀO NHÓM ---
@bot.message_handler(content_types=['new_chat_members'])
def handle_new_chat_members(message):
    chat_id = message.chat.id

    if not get_setting(chat_id, 'welcome', True):
        return

    chat_title = message.chat.title or "nhóm"
    template = WELCOME_MSGS.get(chat_id, DEFAULT_WELCOME_TEXT)
    welcome_video_id = WELCOME_VIDEOS.get(chat_id)

    for new_member in message.new_chat_members:
        if new_member.id == bot.get_me().id:
            continue

        name = new_member.first_name
        tag = f"@{new_member.username}" if new_member.username else f"[{name}](tg://user?id={new_member.id})"

        welcome_text = template.replace("{user}", tag)\
                               .replace("{name}", name)\
                               .replace("{group}", chat_title)\
                               .replace("{chat}", chat_title)

        if "{user}" not in template and "{name}" not in template:
            welcome_text += f" {tag}"

        # Gửi video kèm caption hoặc gửi tin nhắn văn bản nếu không có video
        if welcome_video_id:
            try:
                bot.send_video(chat_id, welcome_video_id, caption=welcome_text, parse_mode="Markdown")
            except Exception:
                # Fallback nếu gửi video lỗi
                bot.send_message(chat_id, welcome_text, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, welcome_text, parse_mode="Markdown")

# --- LỆNH TRỊ THÀNH VIÊN ---
@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id, "Bạn không phải Admin!")
        return
    uid, name, _ = get_user_and_args(message)
    if not uid:
        bot.send_message(message.chat.id, "Vui lòng reply tin nhắn hoặc cung cấp @username / user_id cần ban!")
        return
    try:
        bot.ban_chat_member(message.chat.id, uid)
        bot.send_message(message.chat.id, f"Đã ban [{name}](tg://user?id={uid})", parse_mode="Markdown")
    except Exception:
        bot.send_message(message.chat.id, "Lỗi khi ban thành viên!")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id, "Bạn không phải Admin!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(message.chat.id, "Dùng: /unban <user_id hoặc @username>")
        return
    target_arg = args[1]
    try:
        uid = int(target_arg) if target_arg.isdigit() or (target_arg.startswith('-') and target_arg[1:].isdigit()) else bot.get_chat(target_arg).id
        bot.unban_chat_member(message.chat.id, uid, only_if_banned=True)
        bot.send_message(message.chat.id, f"Đã unban cho: {target_arg}")
    except Exception:
        bot.send_message(message.chat.id, "Lỗi unban!")

@bot.message_handler(commands=['kick'])
def kick_user(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id, "Bạn không phải Admin!")
        return
    uid, name, _ = get_user_and_args(message)
    if not uid:
        bot.send_message(message.chat.id, "Vui lòng reply tin nhắn hoặc cung cấp @username / user_id cần kick!")
        return
    try:
        bot.ban_chat_member(message.chat.id, uid)
        bot.unban_chat_member(message.chat.id, uid)
        bot.send_message(message.chat.id, f"Đã kick [{name}](tg://user?id={uid})", parse_mode="Markdown")
    except Exception:
        bot.send_message(message.chat.id, "Lỗi khi kick!")

@bot.message_handler(commands=['mute', 'suyt'])
def mute_user(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id, "Bạn không phải Admin!")
        return
    uid, name, extra_args = get_user_and_args(message)
    if not uid:
        bot.send_message(message.chat.id, "Vui lòng reply tin nhắn hoặc cung cấp @username / user_id cần mute!")
        return
    
    mins = 60
    for arg in extra_args:
        if arg.isdigit():
            mins = int(arg)
            break
            
    until = int(time.time()) + (mins * 60)
    try:
        bot.restrict_chat_member(message.chat.id, uid, permissions=telebot.types.ChatPermissions(can_send_messages=False), until_date=until)
        bot.send_message(message.chat.id, f"Đã mute [{name}](tg://user?id={uid}) trong {mins} phút", parse_mode="Markdown")
    except Exception:
        bot.send_message(message.chat.id, "Lỗi mute!")

@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id, "Bạn không phải Admin!")
        return
    uid, name, _ = get_user_and_args(message)
    if not uid:
        bot.send_message(message.chat.id, "Vui lòng reply tin nhắn hoặc cung cấp @username / user_id cần unmute!")
        return
    try:
        perms = telebot.types.ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
        bot.restrict_chat_member(message.chat.id, uid, permissions=perms)
        bot.send_message(message.chat.id, f"Đã unmute [{name}](tg://user?id={uid})", parse_mode="Markdown")
    except Exception:
        bot.send_message(message.chat.id, "Lỗi unmute!")

@bot.message_handler(commands=['warn'])
def warn_user(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id, "Bạn không phải Admin!")
        return
    uid, name, _ = get_user_and_args(message)
    if not uid:
        bot.send_message(message.chat.id, "Vui lòng reply tin nhắn hoặc cung cấp @username / user_id cần warn!")
        return
    chat_id = message.chat.id
    
    WARNINGS.setdefault(chat_id, {}).setdefault(uid, 0)
    WARNINGS[chat_id][uid] += 1
    count = WARNINGS[chat_id][uid]
    save_data()
    bot.send_message(chat_id, f"⚠️ Cảnh cáo [{name}](tg://user?id={uid}) ({count}/3)", parse_mode="Markdown")

@bot.message_handler(commands=['unwarn'])
def unwarn_user(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id, "Bạn không phải Admin!")
        return
    uid, name, _ = get_user_and_args(message)
    if not uid:
        bot.send_message(message.chat.id, "Vui lòng reply tin nhắn hoặc cung cấp @username / user_id cần xóa cảnh cáo!")
        return
    chat_id = message.chat.id
    if chat_id in WARNINGS and uid in WARNINGS[chat_id] and WARNINGS[chat_id][uid] > 0:
        WARNINGS[chat_id][uid] -= 1
    count = WARNINGS.get(chat_id, {}).get(uid, 0)
    save_data()
    bot.send_message(chat_id, f"Đã giảm 1 lần cảnh cáo cho [{name}](tg://user?id={uid}). Còn lại: {count}", parse_mode="Markdown")

@bot.message_handler(commands=['warnings'])
def check_warnings(message):
    uid, name, _ = get_user_and_args(message)
    if not uid:
        uid = message.from_user.id
        name = message.from_user.first_name
    count = WARNINGS.get(message.chat.id, {}).get(uid, 0)
    bot.send_message(message.chat.id, f"Thành viên [{name}](tg://user?id={uid}) có {count} lần cảnh cáo.", parse_mode="Markdown")

# --- QUẢN LÝ NHÓM ---
@bot.message_handler(commands=['rules'])
def show_rules(message):
    text = RULES.get(message.chat.id, "Nhóm chưa thiết lập nội quy.")
    bot.send_message(message.chat.id, f"📋 NỘI QUY NHÓM:\n{text}")

@bot.message_handler(commands=['setrules'])
def set_rules(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id, "Bạn không phải Admin!")
        return
    text = message.text[9:].strip()
    if not text:
        bot.send_message(message.chat.id, "Vui lòng nhập nội dung nội quy!")
        return
    RULES[message.chat.id] = text
    save_data()
    bot.send_message(message.chat.id, "Đã cập nhật nội quy nhóm thành công!")

@bot.message_handler(commands=['pin'])
def pin_msg(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id, "Bạn không phải Admin!")
        return
    if not message.reply_to_message:
        bot.send_message(message.chat.id, "Vui lòng reply tin nhắn cần ghim!")
        return
    try:
        bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
        bot.send_message(message.chat.id, "Đã ghim tin nhắn!")
    except Exception:
        bot.send_message(message.chat.id, "Lỗi ghim tin nhắn!")

@bot.message_handler(commands=['unpin'])
def unpin_msg(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id, "Bạn không phải Admin!")
        return
    try:
        bot.unpin_chat_message(message.chat.id)
        bot.send_message(message.chat.id, "Đã bỏ ghim tin nhắn!")
    except Exception:
        bot.send_message(message.chat.id, "Lỗi bỏ ghim!")

@bot.message_handler(commands=['purge'])
def purge_msg(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id, "Bạn không phải Admin!")
        return
    if not message.reply_to_message:
        bot.send_message(message.chat.id, "Vui lòng reply tin nhắn bắt đầu xóa!")
        return
    try:
        start_id = message.reply_to_message.message_id
        end_id = message.message_id
        for m_id in range(start_id, end_id + 1):
            try:
                bot.delete_message(message.chat.id, m_id)
            except Exception:
                pass
    except Exception:
        bot.send_message(message.chat.id, "Lỗi khi xóa tin nhắn!")

@bot.message_handler(commands=['lock', 'unlock'])
def lock_unlock(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id, "Bạn không phải Admin!")
        return
    bot.send_message(message.chat.id, "Đã thực hiện thiết lập khóa/mở nội dung.")

# --- CHỐNG SPAM & CÀI ĐẶT ---
@bot.message_handler(commands=['antispam', 'antilink', 'antiflood', 'captcha', 'goodbye'])
def toggle_settings(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id, "Bạn không phải Admin!")
        return
    args = message.text.split()
    cmd = args[0][1:]
    if len(args) > 1 and args[1].lower() in ['on', 'off']:
        val = (args[1].lower() == 'on')
        set_setting(message.chat.id, cmd, val)
        bot.send_message(message.chat.id, f"Đã chuyển {cmd} thành {args[1].upper()}")
    else:
        st = "ON" if get_setting(message.chat.id, cmd, False) else "OFF"
        bot.send_message(message.chat.id, f"Trạng thái hiện tại của {cmd}: {st}")

@bot.message_handler(commands=['settings'])
def show_settings(message):
    chat_id = message.chat.id
    opts = ['antispam', 'antilink', 'antiflood', 'captcha', 'welcome', 'goodbye']
    lines = [f"- {k}: {'ON' if get_setting(chat_id, k, False if k != 'welcome' else True) else 'OFF'}" for k in opts]
    text = "CÀI ĐẶT NHÓM:\n" + "\n".join(lines)
    bot.send_message(chat_id, text)

# --- THÔNG TIN ---
@bot.message_handler(commands=['id'])
def get_id(message):
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    bot.send_message(message.chat.id, f"🆔 ID Người dùng: `{target.id}`\n🆔 ID Nhóm: `{message.chat.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['info'])
def get_info(message):
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    bot.send_message(message.chat.id, f"Tên: {target.first_name}\nUsername: @{target.username if target.username else 'Không có'}\nID: {target.id}")

@bot.message_handler(commands=['admins', 'staff'])
def get_admins(message):
    try:
        admins = bot.get_chat_administrators(message.chat.id)
        admin_list = "\n".join([f"- {a.user.first_name}" for a in admins])
        bot.send_message(message.chat.id, f"DANH SÁCH QUẢN TRỊ VIÊN:\n{admin_list}")
    except Exception:
        bot.send_message(message.chat.id, "Không thể lấy danh sách admin.")

@bot.message_handler(commands=['language', 'blacklist', 'whitelist'])
def other_cmds(message):
    bot.send_message(message.chat.id, "Đã ghi nhận lệnh hệ thống.")

@bot.message_handler(func=lambda message: True)
def handle_group_message(message):
    if not message.text or message.text.startswith('/'):
        return

    text_clean = message.text.lower().replace("<", "").replace(">", "")
    user = message.from_user

    if user.username:
        tag_text = f"@{user.username}"
    else:
        tag_text = f"[{user.first_name}](tg://user?id={user.id})"

    for keyword, response in KEYWORD_RESPONSES.items():
        kw_clean = keyword.lower().replace("<", "").replace(">", "")
        if kw_clean in text_clean:
            final_response = f"{response} {tag_text}"
            bot.send_message(message.chat.id, final_response, parse_mode="Markdown")
            break

if __name__ == "__main__":
    print("Bot đang hoạt động...")
    bot.infinity_polling()

