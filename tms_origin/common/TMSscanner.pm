package TMSscanner;

###################################################################################################
#
# TMSscanner.pm
#
###################################################################################################

use strict;

use TMSstr;
use TMScommon;

###################################################################################################
# スキャナー１のIPアドレス設定を取得

sub get_scan1_ip_set
{
  my $scan1_ip = "";

  if( open(IPADDR,'< ../../tmsdata/setting/scanner_ip.txt') ){
    $scan1_ip = <IPADDR>;
    close(IPADDR);

    $scan1_ip =~ s/\n$//;	# 改行コードを削除。
    $scan1_ip =~ s/\s//g;	# スペースを削除。
  }

  return $scan1_ip;
}

###################################################################################################

sub save_scan1_ip_set
{
  my ($scan1_ip) = @_;

  &TMScommon::make_dir('../../tmsdata');
  &TMScommon::make_dir('../../tmsdata/setting');

  my $setfile = '../../tmsdata/setting/scanner_ip.txt';

  if( length($scan1_ip) > 0 ){
    if( open(IPADDR, "> $setfile") ){
      print IPADDR $scan1_ip;
      close(IPADDR);
    }
  }else{
    unlink $setfile;
  }
}

###################################################################################################
###################################################################################################

my $GET_SCAN_SETTING = 0;  # 設定データ取得済みか

my @SCAN_IP    = ();  # scanner_ip.txt + scan_member.txt
my @LTB3_ID    = ();  # ltb3_id.txt
my @LOOM_SET   = ();  # loom_set.txt
my @SYSTEM_SET = ();  # system_set.txt


## オリジナル保護の為、直接上記変数を読まない事。
sub get_scan_ip
{
  &get_scan_setting();
  return @SCAN_IP;
}

sub get_ltb3_id
{
  &get_scan_setting();
  return @LTB3_ID;
}

sub get_loom_set
{
  &get_scan_setting();
  return @LOOM_SET;
}

sub get_system_set
{
  &get_scan_setting();
  return @SYSTEM_SET;
}


###################################################################################################
# スキャナー１の設定を取得
# (スキャナーのIP設定の確認も兼ねている)

sub get_scan_setting
{
  # 既に設定データ取得済みなら、処理しない
  if( $GET_SCAN_SETTING ){ return; }
  $GET_SCAN_SETTING = 1;  # 取得済み

  # まず、スキャナー１のIPアドレス取得
  my $scan1_ip = &get_scan1_ip_set();
  if( $scan1_ip eq "" ){ return; }  # スキャナー無しの場合

  @SCAN_IP = ($scan1_ip);  # 注意：&get_scanner_file() の呼び出しより先にセットする事

  ### スキャナー１の設定をまとめて持ってくる(高速化の為) ####

  # ファイル区切り文字列( 英数字 . * - _ のみ使用。スペース不可)

  my $boundary_str = "----------mget-boundary-strings----------";

  my $url = "cgi-bin/mget.cgi?boundary=$boundary_str".
            '&file=..\set\scan_member.txt'.
            '&file=..\set\ltb3_id.txt'.
            '&file=..\set\loom_set.txt'.
            '&file=..\set\system_set.txt';   # (171文字) (255 - 12)文字以内にする事
                                             # 12文字は /TmsScanner/

  my @data = &get_scanner_file( 1, $url );

  ### 取得したデータの分離 ###

  my @scan_member = ();
  my @ltb3_id = ();

  my $boundary_level = 0;
  my $ref_data;

  foreach(@data){
    chomp;
    if( $boundary_level == 1 ){  # 区切り文字の直後の行は、ファイル名
      $boundary_level = 2;
      if(    $_ eq '..\set\scan_member.txt' ){ $ref_data = \@scan_member; }
      elsif( $_ eq '..\set\ltb3_id.txt'     ){ $ref_data = \@ltb3_id;     }
      elsif( $_ eq '..\set\loom_set.txt'    ){ $ref_data = \@LOOM_SET;    }
      elsif( $_ eq '..\set\system_set.txt'  ){ $ref_data = \@SYSTEM_SET;  }
      else{
        $boundary_level = 0;
      }
    }
    elsif( $boundary_level == 2 ){  # データ行
      if( $_ eq $boundary_str ){
        if( $#$ref_data >= 0 ){
          if( length($$ref_data[$#$ref_data]) == 0 ){  # 最後の行が0文字なら
            $#$ref_data = $#$ref_data -1;  # 最後の行を削除(区切り文字の一部なので)
          }
        }
        $boundary_level = 1;
      }else{
        push(@$ref_data, $_);  # データの取り込み
      }
    }else{
      if( $_ eq $boundary_str ){
        $boundary_level = 1;
      }
    }
  }

  #### スキャナー構成ファイルのチェック ####
  my $str_SCANNER_IS_NOT_RUN      = &TMSstr::get_str( 'SCANNER_IS_NOT_RUN'	);
  my $str_SCANNER_COMM_ERROR      = &TMSstr::get_str( 'SCANNER_COMM_ERROR'	);
  my $str_SCANNER_CONFIG_ERROR    = &TMSstr::get_str( 'SCANNER_CONFIG_ERROR'	);
  my $str_CHECK_SCANNER_CONFIG    = &TMSstr::get_str( 'CHECK_SCANNER_CONFIG'	);
  my $str_THIS_IP_IS_NOT_SCANNER1 = &TMSstr::get_str( 'THIS_IP_IS_NOT_SCANNER1'	);

  # 親スキャナー(スキャナー１)の構成ファイルのチェック
  if( $#scan_member < 1 ){
    &disp_scanner_error($str_THIS_IP_IS_NOT_SCANNER1, 1);
    exit;
  }
  if( $scan_member[0] ne "scan_no 1" ){
    &disp_scanner_error($str_THIS_IP_IS_NOT_SCANNER1, 1);
    exit;
  }
  if( $scan_member[1] ne "1 $scan1_ip" ){
    &disp_scanner_error("$str_SCANNER_CONFIG_ERROR<br>\n$str_CHECK_SCANNER_CONFIG", 1);
    exit;
  }

  for( my $i=2; $i<=$#scan_member; $i++ ){
    my ($no,$ip) = split(/\s/,$scan_member[$i],2);

    if( (2 <= $no) and ($no <= 5) and
        ($ip =~ m/^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/)  ){

      $SCAN_IP[($no -1)] = $ip;  # 注意：&get_scanner_file() の呼び出しより先にセットする事

      # 子スキャナー（スキャナー２～５）の構成ファイルと対応を確認
      my @data2 = &get_scanner_file($no,"set/scan_member.txt");

      if( $#data2 >= 1 ){
        if( ($data2[0] eq "scan_no $no") and
            ($data2[1] eq "1 $scan1_ip") ){
          next; # 次のスキャナーへ
        }
      }

      &disp_scanner_error("$str_SCANNER_CONFIG_ERROR<br>\n$str_CHECK_SCANNER_CONFIG", $no);
      exit;
    }
    else{
      &disp_scanner_error("$str_SCANNER_CONFIG_ERROR<br>\n$str_CHECK_SCANNER_CONFIG", 1);
      exit;
    }
  }

  # 不要な ltb3_id を削除（ltb3_id 登録後、スキャナーを削除した場合に対応）
  foreach my $id ( @ltb3_id ){
    if( $id =~ m/^S([1-5])-/ ){
      my $num = $1;
      if( defined($SCAN_IP[$num-1]) ){  # 構成されたスキャナーのみ有効
        push(@LTB3_ID,$id);
      }
    }
  }

}

###################################################################################################
# スキャナーとの通信エラー、スキャナー構成設定エラー表示

sub disp_scanner_error
{
  my ($err_msg,$scan_no) = @_;

  my $lang = &TMSstr::get_lang();

  my $title       = &TMSstr::get_str( 'ERROR'	);
  my $str_SCANNER = &TMSstr::get_str( 'SCANNER'	);
  my $str_MENU    = &TMSstr::get_str( "MENU"	);

  my $tbl_width = 630;
  my $menu_color = '#ED1C24';
  my $body_color = '#FDE1D4';

  print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+2 color=white>$title</font></th>\n".
	"</tr>\n".
	"<tr align=center bgcolor=$body_color><td>\n".
	"<BR><BR>\n";

  print "<font size=+1><B>$err_msg<br>\n";

  if( $scan_no ne "" ){
    my @scan_ip = &get_scan_ip();
    print "<br>( $str_SCANNER $scan_no : $scan_ip[$scan_no -1] )\n";
  }
  print	"</B></font>\n";

  print	"<BR><BR><BR>\n".
	"<NOBR>\n".
	"<A HREF=\"../\"><IMG SRC=\"../image/menu2_$lang.jpg\" width=85 height=27 alt=\"$str_MENU\" border=0></A>\n".
	"</NOBR>\n".
	"<BR><BR><BR><BR>\n".
	"</td></tr>\n".
	"</table><BR>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";
}

###################################################################################################
###################################################################################################

#### httpc.exe のエラー番号(100-999) #####

use constant ERR__PING_TIMEOUT    => 100;
use constant ERR__ARG_ERROR       => 200;
use constant ERR__BAD_HOST_NAME   => 201;
use constant ERR__POST_FILE_ERROR => 210;
use constant ERR__HTTP_NOT_FOUND  => 220;
use constant ERR__HTTP_ERROR      => 300;
use constant ERR__SOCKET_ERROR    => 400;
use constant ERR__PING_ERROR      => 410;
use constant ERR__SYSTEM_ERROR    => 900;

###########################################

sub get_scanner_file
{
  my ( $scan_no, $file, $ref_data ) = @_;

  my @data = ();
  my $err = ERR__SYSTEM_ERROR;

  my @scan_ip = &get_scan_ip();

  my $retry = 0;
  while( 1 ){

    # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
    if( open(PIPE,"..\\bin\\httpc.exe \"$scan_ip[$scan_no -1]\" \"/TmsScanner/$file\" |") ){
      @data = <PIPE>;
      close(PIPE);

      if( $? == 0 ){  # httpc.exe 成功
        foreach(@data){ chomp; }  # 改行コードを取る
        return @data;  # 取得したデータを返す
      }

      # ---- ここからは、httpc.exe 失敗の場合 ----

      if( defined($data[0]) ){
        if( $data[0] =~ m/^(\d{3})\s/ ){  # 先頭が３桁の数字なら
          $err = int($1);
          if( $err == ERR__HTTP_NOT_FOUND ){  # NOT FOUND の場合は、エラー扱いにしない
            if( $retry++ == 0 ){ next; }  # ファイル更新中を考慮し、１回リトライする
            return ();  # 空の配列
          }
        }
      }
    }
    last; # 他のエラーはリトライしない
  }

  # ---- ここまで来たらエラー画面で止まる ----
  my $str_SCANNER_COMM_ERROR = &TMSstr::get_str( 'SCANNER_COMM_ERROR' );
  my $str_SCANNER_IS_NOT_RUN = &TMSstr::get_str( 'SCANNER_IS_NOT_RUN' );

  my $err_msg = $str_SCANNER_COMM_ERROR."<BR>\n";
  if(    $err == ERR__PING_TIMEOUT    ){ $err_msg = $str_SCANNER_IS_NOT_RUN } # pingタイムアウト
  elsif( $err == ERR__PING_ERROR      ){ $err_msg .= "( Network ERROR )";  } # pingエラー
  elsif( $err == ERR__SOCKET_ERROR    ){ $err_msg .= "( Socket ERROR )";   }
  elsif( $err == ERR__HTTP_ERROR      ){ $err_msg .= "( HTTP ERROR )";     }
  else{                                  $err_msg .= "( System ERROR )";   } # システム関係のエラー

  &disp_scanner_error($err_msg, $scan_no);
  exit;
}


###################################################################################################
###################################################################################################

sub get_loom_setting_default
{
  return ( "mac_name"         => "",
           "ubeam_ari"        => 0,
           "style"            => "",
           "beam"             => "",
           "beam_set"         => 0,
           "beam_shrinkage"   => "0.0",
           "ubeam"            => "",
           "ubeam_set"        => 0,
           "ubeam_shrinkage"  => "0.0",
           "use_doff_length"  => 0,
           "doff_length"      => 0,
           "forecast_effic"   => 95,
           "cloth_correction" => "100.0" );
}

###################################################################################################
# 設定ファイルを読み取り、必要な項目だけを２重配列で返す

sub get_loom_setting
{
  my @item_list = @_;

  my @loom_set = ();

  # スキャナーのIPリストを取得
  my @scan_ip = &get_scan_ip();
  if( $#scan_ip < 0 ){ return @loom_set; }  # スキャナー無しの場合


  # 設定値の初期値取得
  my %default_all = &get_loom_setting_default();

  # 引数のチェック & 必要な初期値取得
  my @default = ();
  foreach(@item_list){
    if( exists($default_all{$_}) ){
      push( @default, $default_all{$_} );
    }else{
      print "Data Item Error at &get_loom_setting()\n"; # デバッグ用メッセージ
    }
  }

  # 設定ファイルの読み込み
  my @ltb3_id      = &get_ltb3_id();
  my @loom_set_org = &get_loom_set();


  # 指定された項目だけの２重配列作成（ソートはしない）
  my @data;
  my $mac_id;
  foreach(@loom_set_org){
    if( m/^mac_id (.+)/ ){
      # 前回までの機台のデータ
      if( defined($mac_id) and (&TMScommon::delete_from_list(\@ltb3_id,$mac_id) > 0) ){
        # ２重登録のデータや、ltb3_id に未登録の機台はのデータは、ここで捨てる
        @{$loom_set[$#loom_set+1]} = @data;
      }
      $mac_id = $1;
      @data = ($mac_id,@default);  # 初期化
    }
    else{
      my ($item,$val) = split(/\s/,$_,2);
      if( defined($item) ){
        for( my $i=0; $i<=$#item_list; $i++ ){
          if( $item eq $item_list[$i] ){
            if( ! defined($val) ){ $val = ""; }
            $data[$i+1] = $val;
            last;
          }
        }
      }
    }
  }
  # 最後の機台のデータ
  if( defined($mac_id) and (&TMScommon::delete_from_list(\@ltb3_id,$mac_id) > 0) ){
    @{$loom_set[$#loom_set+1]} = @data;
  }

  # 設定ファイルに無い機台は、初期値を登録
  foreach $mac_id (@ltb3_id){
    @{$loom_set[$#loom_set+1]} = ($mac_id,@default);
  }

  return @loom_set;
}

###################################################################################################

sub update_loom_setting
{
  my ($r_set_list, @item_list) = @_;

  # 全項目名を取得
  my %default = &get_loom_setting_default();
  my @all_item = sort keys %default;

  # 現在の設定値を再読込
  my @loom_set = &get_loom_setting(@all_item);

  # 更新する機台IDのリストを作成
  my @mac_id = ();
  for( my $i=0; $i<=$#$r_set_list; $i++ ){
    $mac_id[$i] = ${$$r_set_list[$i]}[0];
  }

  # 設定された項目を更新する
  foreach my $r_data (@loom_set){
    my $id = $$r_data[0];

    for( my $i=0; $i<=$#mac_id; $i++ ){
      if( $id eq $mac_id[$i] ){
        my @set_data = @{$$r_set_list[$i]};

        for( my $j=0; $j<=$#all_item; $j++ ){
          my $item = $all_item[$j];
          for( my $k=0; $k<=$#item_list; $k++ ){
            if( $item eq $item_list[$k] ){
              $$r_data[$j+1] = $set_data[$k+1];
            }
          }
        }
      }
    }
  }

  ## 機台ID順にソート
  @loom_set = sort { $$a[0] cmp $$b[0] } @loom_set;

  # 設定ファイル用のデータに変換する
  my @loom_set_txt = ();
  foreach my $r_data (@loom_set){
    push( @loom_set_txt, "" );  # 改行
    push( @loom_set_txt, "mac_id $$r_data[0]" );  # ちょっと無理矢理？

    for( my $i=0; $i<=$#all_item; $i++ ){
      push( @loom_set_txt, "$all_item[$i] $$r_data[$i+1]" );
    }
  }

  ## スキャナーのファイルを更新する
  &upload_scanner_file( "all",
                        ["set/loom_set.txt","set/loom_set.update"],
                        \@loom_set_txt,     ["update"] );

}


###################################################################################################
###################################################################################################

sub save_tmp_file
{
  my ($tmp_file,$r_list) = @_;

  if( open(FILE,"> $tmp_file") ){

    foreach my $r_data ( @$r_list ){
      for( my $i=0; $i<=$#$r_data; $i++ ){
        if( $i > 0 ){ print FILE "\t"; }
        print FILE $$r_data[$i];
      }
      print FILE "\n";
    }

    close(FILE);
  }

  return $tmp_file;
}

## -----------------------------------------------------------------

sub load_tmp_file
{
  my ($tmp_file) = @_;

  my @list = ();
  if( open(FILE, "< $tmp_file") ){

    my $i=0;
    while(<FILE>){
      my @data = split(/\t/);
      chomp $data[$#data];     # 最後の要素の改行を取る
      @{$list[$i++]} = @data;  # (要素の数が減らない様にsplitした後にchompする)
    }

    close(FILE);
  }

  return @list;
}


###################################################################################################
# データ更新処理
###################################################################################################

sub upload_scanner_file
{
  my ( $scan_no, $r_file, @r_data ) = @_;

  my @scan_ip = &get_scan_ip();
  if( $scan_no ne "all" ){
    my $ip = $scan_ip[$scan_no -1];
    @scan_ip = ();
    $scan_ip[$scan_no -1] = $ip;  # 対象のIPだけ残す
  }

  my @file = ();
  if( ref($r_file) ){ @file = @$r_file; }
  else{ @file = ($r_file); }  # 参照でない場合


  ### ファイルのパスを変換 ###
  foreach( @file ){
    s/\//\\/g;  # / -> \ に変換
    $_ = "..\\".$_;
  }


  ### boundary 文字列を決める ( 英数字 . * - _ のみ使用。スペース不可) ###

  my $boundary_str = "---------------------------tms2scanner";

  #### 追加ヘッダー ###

  my $header_str = "Content-Type: multipart/form-data; boundary=".$boundary_str;

  #### POSTデータ を一時ファイルに書き込む ####

  my $str_SCANNER_UPLOAD_ERROR = &TMSstr::get_str( 'SCANNER_UPLOAD_ERROR' );
  my $str_SCANNER_IS_NOT_RUN   = &TMSstr::get_str( 'SCANNER_IS_NOT_RUN'	);

  my $post_file = &TMScommon::get_tmp_file_name("scan_post");
  if( ! open(FILE,"> $post_file") ){
    &disp_scanner_error($str_SCANNER_UPLOAD_ERROR, "");
    exit;
  }else{
    binmode(FILE);  # バイナリーモードにする

    for( my $i=0; $i<=$#file; $i++ ){
      print FILE "--".$boundary_str."\r\n";

      print FILE "Content-Disposition: form-data; name=\"file\"; filename=\"$file[$i]\"\r\n";
      print FILE "Content-Type: text/plain\r\n";
      print FILE "\r\n";

      foreach( @{$r_data[$i]} ){
        print FILE $_."\r\n";
      }
    
      print FILE "\r\n".$boundary_str."--\r\n";
    }
    close(FILE);
 }

  #### 各スキャナーに送信 ###

  for( my $i=0; $i<=$#scan_ip; $i++ ){
    if( defined($scan_ip[$i]) ){

      my $err = ERR__SYSTEM_ERROR;
      # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
      if( open(PIPE,"..\\bin\\httpc.exe \"$scan_ip[$i]\" \"/TmsScanner/cgi-bin/file_upload.cgi\" \"$header_str\" $post_file |") ){
        my @result = <PIPE>;
        close(PIPE);

        if( $? == 0 ){  # httpc.exe 成功
          $err = 0;
        }
        elsif( defined($result[0]) ){  # httpc.exe 失敗のエラー番号
          if( $result[0] =~ m/^(\d{3})\s/ ){  # 先頭が３桁の数字なら
            $err = int($1);
          }
        }
      }

      if( $err != 0 ){  # エラーの場合、画面表示して、中断
        unlink( $post_file );

        my $err_msg = $str_SCANNER_UPLOAD_ERROR."<BR>\n";
        if(    $err == ERR__PING_TIMEOUT    ){ $err_msg = $str_SCANNER_IS_NOT_RUN } # pingタイムアウト
        elsif( $err == ERR__PING_ERROR      ){ $err_msg .= "( Network ERROR )";  } # pingエラー
        elsif( $err == ERR__SOCKET_ERROR    ){ $err_msg .= "( Socket ERROR )";   }
        elsif( $err == ERR__HTTP_ERROR      ){ $err_msg .= "( HTTP ERROR )";     }
        elsif( $err == ERR__HTTP_NOT_FOUND  ){ $err_msg .= "( HTTP ERROR -- Not Found -- )"; }
        else{                                  $err_msg .= "( System ERROR )";   } # システム関係のエラー

        &disp_scanner_error($err_msg, ($i+1));
        exit;
      }
    }
  }
  unlink( $post_file );
}

###################################################################################################
###################################################################################################

sub get_unit_setting
{
  my ($r_cloth_unit, $r_beam_unit, $r_density_unit) = @_;

  ## 初期値
  my $cloth_unit   = 0;  # pick
  my $density_unit = 0;  # /cm

  ## 設定ファイルの読み込み
  my @system_set = &get_system_set();

  foreach( @system_set ){
    if   ( m/^length_unit\s+pick$/  ){ $cloth_unit = 0; } # pick
    elsif( m/^length_unit\s+meter$/ ){ $cloth_unit = 1; } # meter
    elsif( m/^length_unit\s+yard$/  ){ $cloth_unit = 2; } # yard

    elsif( m/^density_unit\s+cm$/   ){ $density_unit = 0; } # /cm
    elsif( m/^density_unit\s+inch$/ ){ $density_unit = 1; } # /inch
  }

  my $beam_unit;
  if( $cloth_unit == 0 ){ $beam_unit = 1; }  # pick -> meter
  else{                   $beam_unit = $cloth_unit; }

  $$r_cloth_unit   = $cloth_unit;
  $$r_beam_unit    = $beam_unit;
  $$r_density_unit = $density_unit;
}

# -----------------------------------------------------
# -----------------------------------------------------

sub get_str_length_unit_name
{
  my $str_PICK  = &TMSstr::get_str( "PICK"	);
  my $str_METER = &TMSstr::get_str( "METER"	);
  my $str_YARD  = &TMSstr::get_str( "YARD"	);

  return ($str_PICK, $str_METER, $str_YARD);
}

# -----------------------------------------------------

sub get_str_density_unit_name
{
  my $str_PER_CM   = &TMSstr::get_str( 'PER_CM'		);
  my $str_PER_INCH = &TMSstr::get_str( 'PER_INCH'	);

  return ($str_PER_CM, $str_PER_INCH);
}

# -----------------------------------------------------
# -----------------------------------------------------

sub get_str_length_unit
{
  return ("kpick", "m", "yard");
}

# -----------------------------------------------------

sub get_str_density_unit
{
  return ("/cm", "/inch");
}

###################################################################################################
###################################################################################################




###################################################################################################
1;
