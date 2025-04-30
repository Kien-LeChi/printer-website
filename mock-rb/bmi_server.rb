# ==================================================
# file: bmi_server.rb
# Copyright: 2011-2015 Brother Industries, Ltd.
# ==================================================
require "rubygems"
require "sinatra"
require "rexml/document" # standard XML parser
require "sinatra/cookies" # for using cookie
#-------------------------------------------------
# Methods
#-------------------------------------------------
def clear_cookie
  cookies[:height] = nil
  cookies[:weight] = nil
end

#
#=== parse_user_input
# Parse Event-message-XML including <UserInput> tree and return key-value data
#
#xml :: [String] SerioEvent XML such like
# <SerioEvent><UserInput><UserInputValues>
# <KeyValueData>
# <Key>keyA</Key>
# <Value>valueA</Value>
# </KeyValueData>
# <KeyValueData>
# <Key>keyB</Key>
# <Value>valueB</Value>
# </KeyValueData>
# </UserInputValues></UserInput></SerioEvent>
def parse_user_input(xml)
  array = Array.new
  doc = REXML::Document.new(xml)
  begin
    doc.elements.each("SerioEvent/UserInput/UserInputValues/KeyValueData") { |kv|
      array << {
        :key => kv.elements["Key"].text,
        :value => kv.elements["Value"].text,
      }
    }
  rescue
    puts "PARSE ERROR OCCURRED."
  end
  array
end

#
#=== save_session
# Parse SerioEvent XML and set cookies.
#
#params :: [Hash] parameters
def save_session(params)
  # Inherit existing cookies to next session.
  cookies.each do |k, v|
    cookies[k] = v
  end
  return unless params[:xml]
  # new value
  keyvalues = parse_user_input(params[:xml].to_s) # Event message is always stored
  # as value of "xml".
  keyvalues.each { |kv|
    case kv[:key]
    when "p_height"
      cookies[:height] = kv[:value].to_f / 100.0 # set cookie
    when "p_weight"
      cookies[:weight] = kv[:value].to_f # set cookie
    end
  }
end

#
#=== build_ui_weight
# Build <NumericalArea> UiScript for querying weight info.
#
def build_ui_weight
  @param = {
    :submit => "./height", # assign "POST to ./height" to submit button.
    :back => "./init", # assign "GET ./init" to back button.
    :objtitle => "Put your weight in [kg]",
    :id => "p_weight", # parameter name
    :min => "10",
    :max => "200",
  }
  content_type :xml
  erb :numinput # use "numinput.erb" template
end

#
#=== build_ui_height
# Build <NumericalArea> UiScript for querying height info.
#
def build_ui_height
  @param = {
    :submit => "./result",
    :back => "./weight",
    :objtitle => "Put your height in [cm]",
    :id => "p_height",
    :min => "100",
    :max => "250",
  }
  content_type :xml
  erb :numinput # use <NumericalArea> template
end

#-------------------------------------------------
# Routes
#-------------------------------------------------
get "/init" do
  clear_cookie()
  build_ui_weight()
end
post "/init" do
  clear_cookie()
  build_ui_weight()
end
get "/weight" do
  build_ui_weight()
end
post "/weight" do
  build_ui_weight()
end
get "/height" do
  build_ui_height()
end
post "/height" do
  save_session(params)
  build_ui_height()
end

post "/result" do
  save_session(params)
  @param = {
    :submit => "./init",
    :objtitle => "Your BMI",
  }
  value_not_enough = false
  unless cookies[:height]
    puts "NO DATA :height"
    value_not_enough = true
  end
  unless cookies[:weight]
    puts "NO DATA :weight"
    value_not_enough = true
  end
  if value_not_enough
    @param[:msgbody] = "Error: parameters not enough."
  else
    # Calculate BMI
    (weight, height) = [cookies[:weight].to_f, cookies[:height].to_f]
    bmi = weight / (height * height) # get cookie and calculate BMI
    bmi = bmi.round(1)
    @param[:msgbody] = "Your BMI is #{bmi}.¥n"
    if bmi < 18.5
      @param[:msgbody] += "Underweight."
    elsif bmi < 25
      @param[:msgbody] += "Normal."
    elsif bmi < 30
      @param[:msgbody] += "Overweight."
    else
      @param[:msgbody] += "Obese."
    end
  end
  content_type :xml
  erb :message # use <Message> template
end

not_found do
  @param = {
    :submit => "./init",
    :back => "./init",
    :objtitle => "UNDEFINED",
    :msgbody => "The page you requested does not exist.",
  }
  content_type :xml
  return erb :message
end
