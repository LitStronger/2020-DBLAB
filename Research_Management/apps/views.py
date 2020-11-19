from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from django.contrib import auth
from django.contrib.auth.decorators import login_required

from apps import myforms
from apps import models




# 测试函数
def test(request):
    return render(request, 'base.html')

# 注册
# todo：只有管理员可以注册，因此后期还得加一个if判断
def createuser(request):
    # 产生一个空对象
    form_obj = myforms.MyRegForm()
    if request.method == 'POST':
        back_dic = {'code':1000, 'msg':''}
        # 校验数据
        form_obj = myforms.MyRegForm(request.POST)
        if form_obj.is_valid():
            # form_obj.cleaned_data  # {'username':'','password':'','confirm_password':'','email':''}
            clean_data = form_obj.cleaned_data
            clean_data.pop('confirm_password')  #  {'username':'','password':'','email':''}
            models.UserInfo.objects.create_user(**clean_data)
            # 目前想法是注册完之后弹出注册完成的框，不跳转
            # back_dic['url'] = '/login/'
        else:
            back_dic['code'] = 2000
            back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)
    return render(request, 'createuser.html', locals())
    
# 登录
def login(request):
    if request.method == 'POST':
        back_dic = {'code':1000, 'msg':''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        # 1 先校验验证码是否正确
        if request.session.get('code').upper() == code.upper():
            # 2 校验用户名和密码是否正确
            user_obj = auth.authenticate(username=username, password=password)
            if user_obj:
                # 3 保存用户登录状态
                auth.login(request, user_obj)
                back_dic['url'] = '/home/'
            else:
                back_dic['code'] = 2000
                back_dic['msg'] = '用户名或密码错误'
        else:
            back_dic['code'] = 3000
            back_dic['msg'] = '验证码错误'
        return JsonResponse(back_dic)
    return render(request, 'login.html')

# 添加
def insert(request):
    return render(request, 'insert.html', locals())

# 查询
def query(request):
    return render(request, 'query.html', locals())

# 详细信息
def detail(request):
    return render(request, 'detail.html', locals())


# 主页
def home(request):
    # 这里以后要加上展现在主页的那些论文提交结果
    
    return render(request,'home.html', locals())

# 图片验证码相关

from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO


def get_code(request):
    '''生成验证码，在图片上写字'''
    def get_random_rgb():
        '''随机生成RGB颜色'''
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    img_obj = Image.new('RGB', (310, 35), get_random_rgb())
    img_draw = ImageDraw.Draw(img_obj)  # 生成一个画笔对象
    img_font = ImageFont.truetype('static/font/111.ttf', 30)  # 字体的样式
    """
    所有的字体样式都是由.ttf结尾的文件控制的
    """
    # 随机生成验证码  a~z  A~Z  0~9
    code = ''
    for i in range(5):
        random_upper = chr(random.randint(65, 90))
        random_lower = chr(random.randint(97, 122))
        random_int = str(random.randint(0, 9))
        temp = random.choice([random_upper, random_lower, random_int])
        # 将产生的随机字符写到图片上
        img_draw.text((i*45+45,0), temp, get_random_rgb(), img_font)
        code += temp
    print(code)
    # 将随机验证码存储取来  以便其他函数调用
    request.session['code'] = code

    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())
