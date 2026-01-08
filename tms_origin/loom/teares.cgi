#!/usr/bin/perl
use strict;
use warnings;
use CGI;
use JSON;
use lib 'C:/Apache2/htdocs/tms/common';
require 'http_header.pm';
require 'TMSstr.pm';
require 'TMScommon.pm';
require 'TMSscanner.pm';

my $q = CGI->new;

# Captura o parâmetro ?json=1
my $json_mode = $q->param('json') || 0;

# Aqui você chama sua função que obtém o status dos teares:
# Substitua pela função real que retorna os dados dos teares.
# Exemplo genérico:
my @teares = (
    { id => "00001", artigo => 2220, status => "em Operação", eficiencia => 90, rpm => 956 },
    { id => "00002", artigo => 2220, status => "Trama", eficiencia => 90, rpm => 956 },
    { id => "00003", artigo => 2220, status => "em Operação", eficiencia => 85, rpm => 956 },
    { id => "00004", artigo => 2220, status => "Desligada", eficiencia => 0, rpm => 0 },
);

if ($json_mode) {
    print "Content-type: application/json\n\n";
    print encode_json(\@teares);
    exit;
}

# HTML antigo abaixo (caso alguém ainda acesse direto)
print "Content-type: text/html\n\n";
print "<html><body><h1>Status dos Teares</h1>";
foreach my $t (@teares) {
    print "<p>Tear $t->{id} - $t->{status}</p>";
}
print "</body></html>";
