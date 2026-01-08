package TMSstr;

################################################################################
#
# TMSstr.pm
#
################################################################################

use strict;

###################################################################################################
# 言語設定値ファイル関係
###################################################################################################

sub get_lang_set
{
  my $lang_set = "";
  my $setting_path = 'setting';  # for /tms/index.cgi

  unless( -d $setting_path ){ $setting_path = '../setting'; }

  if( open(FILE,"< $setting_path/language.txt") ){
    while(<FILE>){
      $_ =~ s/\n$//;		# 改行コードを削除。
      $lang_set = $_;
      last;
    }
    close(FILE);
  }
  if( length($lang_set) == 0 ){ $lang_set = 'en'; }  # デフォルト
  return $lang_set;
}

################################################################################

sub save_language
{
  my( $newlang ) = @_;

  open(FILE, '> language.txt');

  print FILE "$newlang\n";

  close(FILE);
}

################################################################################

sub get_lang_list
{
  return ('en','zh-cn','zh-tw','ko','ja','pt' );
}

sub get_lang_name
{
  return ('English','Chinese','Tiwanese','Korean','Japanese','Portuguese' );
}

###################################################################################################
# 翻訳文字の読み出し
###################################################################################################

my $LANG = "";
my %str = ();

sub load_str_file
{
  my($lang) = @_;

  if( $LANG ne "" ){ return; }  # 一度、言語設定されたら変更不可
  $LANG = $lang;

  # 各言語の文字列データを読み込む
  if(    $lang eq 'ja'    ){ require "str_ja.pm";    }
  elsif( $lang eq 'zh-cn' ){ require "str_zh-cn.pm"; }
  elsif( $lang eq 'zh-tw' ){ require "str_zh-tw.pm"; }
  elsif( $lang eq 'ko'    ){ require "str_ko.pm";    }
  elsif( $lang eq 'pt'    ){ require "str_pt.pm";    }
  else{                      require "str_en.pm";    } # デフォルト

  %str = &load_str();  # in str_???.pm
}

################################################################################
# 設定済み言語を取得（エラー画面等で使う為）

sub get_lang
{
  return $LANG;
}

################################################################################

sub get_str
{
  my($key) = @_;

  if( exists($str{$key}) ){ return $str{$key} };

  return "!!".$key."!!";
}

###################################################################################################
# 停止原因
###################################################################################################

my %stop_cause_jat710 = ();
my %stop_cause_lwt710 = ();

sub load_stop_cause
{
  %stop_cause_jat710 = &load_stop_cause_str_jat710();  # in str_???.pm
  %stop_cause_lwt710 = &load_stop_cause_str_lwt710();  # in str_???.pm
}

################################################################################

sub get_stop_cause
{
  my ( $code, $mac_type ) = @_;

  if( $mac_type eq "JAT710" ){
    if( $code ne "" ){
      $code = lc($code);  # アルファベットは小文字に変換

      if( exists($stop_cause_jat710{$code}) ){
        return $stop_cause_jat710{$code};
      }
    }
    return $stop_cause_jat710{'OTHER_STOP'};
  }

  if( $mac_type eq "LWT710" ){
    if( $code ne "" ){
      $code = lc($code);  # アルファベットは小文字に変換

      if( exists($stop_cause_lwt710{$code}) ){
        return $stop_cause_lwt710{$code};
      }
    }
    return $stop_cause_lwt710{'OTHER_STOP'};
  }

  return "Undefined Message";
}

################################################################################
1;
