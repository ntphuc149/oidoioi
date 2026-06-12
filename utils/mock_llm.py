"""Mock LLM for AI/ML Q&A Agent — no API key required."""
import time
import random

MOCK_RESPONSES = {
    "machine learning": [
        "Machine Learning là một nhánh của AI cho phép máy tính học từ dữ liệu mà không cần lập trình cụ thể. Có 3 loại chính: Supervised Learning, Unsupervised Learning, và Reinforcement Learning.",
        "Machine Learning hoạt động bằng cách tìm patterns trong dữ liệu. Model được train trên tập training data, sau đó dự đoán trên dữ liệu mới.",
    ],
    "deep learning": [
        "Deep Learning là một subset của Machine Learning sử dụng Neural Networks nhiều lớp (deep). Rất hiệu quả cho image recognition, NLP, và speech recognition.",
        "Deep Learning cần nhiều dữ liệu và tài nguyên tính toán hơn ML truyền thống, nhưng đạt kết quả vượt trội trong nhiều bài toán phức tạp.",
    ],
    "neural network": [
        "Neural Network được lấy cảm hứng từ não người, gồm các neurons kết nối với nhau. Mỗi neuron nhận input, áp dụng activation function, và truyền output đến layer tiếp theo.",
        "Các loại Neural Network phổ biến: CNN (image), RNN/LSTM (sequence), Transformer (NLP). Mỗi loại phù hợp với một dạng dữ liệu khác nhau.",
    ],
    "transformer": [
        "Transformer là kiến trúc được giới thiệu trong paper 'Attention Is All You Need' (2017). Nó là nền tảng của các mô hình GPT, BERT, và hầu hết LLM hiện đại.",
        "Transformer dùng cơ chế Self-Attention để nắm bắt mối quan hệ giữa các token trong sequence, hiệu quả hơn RNN vì có thể xử lý song song.",
    ],
    "llm": [
        "Large Language Model (LLM) là các mô hình ngôn ngữ lớn được train trên lượng dữ liệu khổng lồ. Ví dụ: GPT-4, Claude, Gemini. Chúng có khả năng sinh text, dịch thuật, lập trình, và hơn thế nữa.",
        "LLM hoạt động bằng cách dự đoán token tiếp theo dựa trên context. Dù đơn giản về nguyên lý, nhưng với scale đủ lớn chúng nổi lên các khả năng mới (emergent abilities).",
    ],
    "overfitting": [
        "Overfitting xảy ra khi model học quá kỹ training data, bao gồm cả noise, khiến nó không generalize tốt trên data mới. Nhận biết: train loss thấp nhưng validation loss cao.",
        "Cách xử lý overfitting: thêm Dropout, L1/L2 regularization, data augmentation, early stopping, hoặc thu thập thêm training data.",
    ],
    "python": [
        "Python là ngôn ngữ phổ biến nhất cho AI/ML nhờ ecosystem phong phú: NumPy, Pandas, Scikit-learn, TensorFlow, PyTorch. Cú pháp đơn giản giúp tập trung vào thuật toán.",
        "Các thư viện Python quan trọng cho ML: Scikit-learn (classical ML), PyTorch/TensorFlow (deep learning), HuggingFace Transformers (LLM), LangChain (LLM apps).",
    ],
    "gradient": [
        "Gradient Descent là thuật toán tối ưu hóa cốt lõi trong ML. Nó cập nhật weights theo hướng ngược chiều gradient của loss function để minimize loss.",
        "Các biến thể của Gradient Descent: SGD (Stochastic), Mini-batch GD, Adam, RMSprop. Adam thường là lựa chọn mặc định tốt cho deep learning.",
    ],
    "default": [
        "Đó là một câu hỏi thú vị về AI/ML! Trong production, tôi sẽ kết nối với OpenAI/Anthropic để trả lời chi tiết hơn. Hiện tại tôi đang chạy ở chế độ mock.",
        "AI và Machine Learning là lĩnh vực rộng lớn với nhiều khái niệm thú vị. Hãy hỏi tôi về: Neural Networks, Deep Learning, LLM, Python cho ML, hoặc các thuật toán cụ thể!",
        "Tôi là AI/ML Q&A Agent. Tôi có thể giải thích các khái niệm như Transformer, Gradient Descent, Overfitting, và nhiều chủ đề AI/ML khác.",
    ],
}


def ask(question: str, delay: float = 0.1) -> str:
    time.sleep(delay + random.uniform(0, 0.05))
    question_lower = question.lower()
    for keyword, responses in MOCK_RESPONSES.items():
        if keyword in question_lower:
            return random.choice(responses)
    return random.choice(MOCK_RESPONSES["default"])
