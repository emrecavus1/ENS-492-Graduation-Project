require 'json'

resultset = JSON.parse(File.read('coverage/.resultset.json'))
run = resultset.values.first
result = run['result']

puts "Overall statement coverage: #{result['covered_percent']}%"
