# extended Array
class Array
  def odd_number
    select(&:odd?)
  end

  def times_of(n)
    select { |a| a % n == 0 }
  end
end

ary = 1.upto(20).to_a
# => [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
ary.odd_number.times_of(3)
# => [3, 9, 15]
