#include <iostream>
#include <cstddef>
#include <iomanip> // Required for std::hex and std::setw

// constexpr std::byte terminal{0xFF};
constexpr uint32_t MAX_BYTES = 100000;

bool isLittleEndian() {
    int num = 1;
    // Cast the int address to a char pointer to look at the first byte
    char* bytePtr = reinterpret_cast<char*>(&num);
    
    return (*bytePtr == 1);
}

class Serializer {
public:
    Serializer(uint32_t max_bytes) {
        capcity = max_bytes;
        offset = 0;

        buffer.reserve(max_bytes);
    }
    template<typename T>
    requires std::is_trivially_copyable_v<T>
    void write(const T& value)
    {
        std::memcpy(buffer.data() + offset,
                    &value,
                    sizeof(T));

        offset += sizeof(T);
    } 

    const std::vector<std::byte>& bytes() const {
        return buffer;
    }

    void snacks_print(){ 
        for(uint32_t i = 0; i<offset; i++){ 
            std::cout << "0x" 
                    << std::hex << std::setw(2) << std::setfill('0') 
                    << static_cast<int>(buffer[i]) << "\t";
        } 
        std::cout << "\n"; 
    }
private:
    uint32_t offset, capcity; 
    std::vector<std::byte> buffer;
};

int main() {
    if (isLittleEndian()){
        std::cout << "little endian\n";
    } else {
        std::cout << "big endian\n";
    }
    std::cout << "hello world!\n"; 
    Serializer snacks(MAX_BYTES);

    int a = 100;
    int b = 200;
    float c = 2.0f;

    snacks.write(a);
    snacks.snacks_print();
    snacks.write(b);
    snacks.snacks_print();
    snacks.write(c);
    snacks.snacks_print();

    return 0;
}