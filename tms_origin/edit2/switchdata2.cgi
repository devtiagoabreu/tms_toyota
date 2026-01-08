#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;

use TMSswitchdata;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

#----------------------------------------------------------------------------------------------------
# データ名のリスト作成

my $rootdir = "..\\..";

my @data_name_list = ();  # データ名のリスト

&TMSswitchdata::get_save_data_name(\@data_name_list);  # 保存データ名

my $current_name = &TMSswitchdata::get_current_data_name(\@data_name_list);  # 現在使用中のデータ名

# ---------------------------------------------------------------------------------------------------

my $html = new CGI;

my $mode = $html->param('mode');

# -------------------------------------------------------------------------------
# データ切替

if( $mode eq 'switch' ){

  my $dataname = $html->param('dataname');
  if( length($dataname) > 0 ){

    my $old_name;
    my $dir_name;

    # 現在データを名前を付けて保存
    if( length($current_name) > 0 ){
      $old_name = "tmsdata";
      $dir_name = "tmsdata.$current_name";
      &rename_dir( $old_name, $dir_name );		# ディレクトリ名を変更
    }

    # 選択されたデータを現在データへ
    $old_name = "tmsdata.$dataname";
    $dir_name = "tmsdata";
    &rename_dir( $old_name, $dir_name );		# ディレクトリ名を変更

  }
}

# ------------------------------------------------------------------------------
# データ名の変更

elsif( $mode eq 'rename' ){

  my $dataname = $html->param('dataname');
  my $newname  = $html->param('newname');

  $newname =~ s/\s+/ /g;		# ２個以上のスペースを１個にする。
  $newname =~ s/^\s//;			# 先頭のスペースを削除。
  $newname =~ s/\s$//;			# 行端のスペースを削除。
  $newname =~ s/[ \\\/:,;*?"<>|]/_/g;	# ファイル名に使え無い文字を _ に変換

  if( (length($dataname) > 0) && (length($newname) > 0) ){

    if( &duplicate_check($newname) == 0 ){	# 名前の重複チェック

      my $old_name;
      my $dir_name;

      if( $dataname eq $current_name ){	# 現在データ
        $dir_name = "tmsdata";
      }
      else{				# 保存データ
        $old_name = "tmsdata.$dataname";
        $dir_name = "tmsdata.$newname";
        &rename_dir( $old_name, $dir_name );		# ディレクトリ名を変更
      }

      &save_name_data( $dir_name, $newname );		# 名前を保存
    }
  }
}

# ------------------------------------------------------------------------------
# 新規データ領域の作成

elsif( $mode eq 'create' ){

  my $newname = $html->param('newname');

  $newname =~ s/\s+/ /g;		# ２個以上のスペースを１個にする。
  $newname =~ s/^\s//;			# 先頭のスペースを削除。
  $newname =~ s/\s$//;			# 行端のスペースを削除。
  $newname =~ s/[ \\\/:,;*?"<>|]/_/g;	# ファイル名に使え無い文字を _ に変換

  if( length($newname) > 0 ){

    if( &duplicate_check($newname) == 0 ){	# 名前の重複チェック

      my $old_name;
      my $dir_name;

      # 現在データを名前を付けて保存
      if( length($current_name) > 0 ){
        $old_name = "tmsdata";
        $dir_name = "tmsdata.$current_name";
        &rename_dir( $old_name, $dir_name );		# ディレクトリ名を変更
      }

      # 現在データとして新規作成
      $dir_name = "tmsdata";
      unless( -d "$rootdir\\$dir_name" ){
        if( -f "$rootdir\\$dir_name" ){ unlink("$rootdir\\$dir_name"); }	# 同名のファイルは消す
        mkdir( "$rootdir\\$dir_name" );			# 作成
        &save_name_data( $dir_name, $newname );		# 名前を保存
      }
    }
  }
}

# ------------------------------------------------------------------------------
# データの削除

elsif( $mode eq 'delete' ){

  my $dataname = $html->param('dataname');
  if( length($dataname) > 0 ){

    my $dir_name;
    if( $dataname eq $current_name ){ $dir_name = "tmsdata"; }			# 現在のデータ
    else{                             $dir_name = "tmsdata.$dataname"; }	# 保存されたデータ

    if( -d "$rootdir\\$dir_name" ){
      # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
      system( "RMDIR /S /Q \"$rootdir\\$dir_name\"" );		# 削除
    }
  }
}

# ------------------------------------------------------------------------------
# リダイレクトページの表示

print	"<HTML><HEAD><META HTTP-EQUIV=\"Refresh\" CONTENT=\"0; URL=switchdata.cgi\"></HEAD>\n".
	"<BODY bgcolor=#C7C4E2></BODY></HTML>";

exit;

###################################################################################################

sub duplicate_check
{
  my ($name) = @_;

  # 文字列を大文字に変換(ディレクトリ名は、大文字小文字の区別無い為）
  my $uc_name = uc($name);
  my @uc_list = ();
  foreach(@data_name_list){ my $d = uc($_); push(@uc_list,$d); }

  # 比較
  my $dup = 0;
  foreach(@uc_list){ if( $uc_name eq $_ ){ $dup = 1; last; } }

  return $dup;
}

# ------------------------------------------------------------------------------

sub rename_dir
{
  my( $old_name, $new_name ) = @_;

  if( -d "$rootdir\\$old_name" ){

    unless( -d "$rootdir\\$new_name" ){
      if( -f "$rootdir\\$new_name" ){ unlink("$rootdir\\$new_name"); }	# 同名のファイルがあったら消す
      # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
      system( "RENAME \"$rootdir\\$old_name\" \"$new_name\"" );		# 名前変更
    }
  }
}

# ------------------------------------------------------------------------------

sub save_name_data
{
  my ( $dir_name, $name ) = @_;

  if( open( NAME, "> $rootdir\\$dir_name\\savename.txt" ) ){	# 名前を保存
    print NAME "$name";
    close(NAME);
  }
}

# ------------------------------------------------------------------------------
