# -*- coding: utf-8 -*-
import os
import config
import tempfile
import xml.etree.ElementTree as etree
from datetime import datetime
import time
import logging
logger = logging.getLogger(__name__)

class Exporter():

    def verify_elem(self, elem, deptor):
        if not elem['lines']:
            raise Exception('Ingen vare linier på faktura {}'.format(elem['key']))
        if not elem['customer_order_number'].strip():
            #raise Exception('Kundeordrenummer mangler på faktura {}'.format(elem['key']))
            pass
        if not deptor['gln'].isdigit():
            raise Exception('Kunde ean-nummer {} er ikke et tal, faktura {}'.format(deptor['gln'], elem['key']))

    def validate_line(self, i):
        gln = i.get('gln_number', None)
        if not gln:
            raise Exception('GLN-nummer mangler på vare {}'.format(i['item_number']))
        if not gln.isdigit():
            raise Exception('GLN-nummer  på vare {} er ugyldigt'.format(i['item_number']))
        # note that we round to ignore half cents/oere
        if round(i['total_without_tax'] * 1.25) != i['total_with_tax']:
            raise Exception('Inkl. moms er forskellig fra ex. moms. på vare {}'.format(i['item_number']))

class OIOXML(Exporter):

    def __init__(self):

        self.i_line='''
            \t\t<InvoiceLine>
                <ID>1</ID>
                <InvoicedQuantity unitCode="PCE" unitCodeListAgencyID="UN/UOM">100</InvoicedQuantity>
                <LineExtensionAmount>1000</LineExtensionAmount>
                <Item>
                    <ID schemeID="EAN-13">5705822001451</ID>
                    <Description></Description>
                    <Tax>
                        <RateCategoryCodeID>VAT</RateCategoryCodeID>
                        <TypeCode>VAT</TypeCode>
                        <RatePercentNumeric>25</RatePercentNumeric>
                    </Tax>
                </Item>
                <BasePrice>
                    <PriceAmount>10</PriceAmount>
                </BasePrice>
            </InvoiceLine>\r\n
        '''
        self.template = '''
            <Invoice>
                    <ID>2345671</ID>
                    <IssueDate>2004-12-31</IssueDate>
                    <TypeCode>PIETEST</TypeCode>
                    <InvoiceCurrencyCode>DKK</InvoiceCurrencyCode>
                    <BuyersReferenceID schemeID="EAN"></BuyersReferenceID>
                    <ReferencedOrder>
                            <BuyersOrderID></BuyersOrderID>
                            <IssueDate></IssueDate>
                    </ReferencedOrder>
                    <BuyerParty>
                            <ID schemeID="EAN">5790000088522</ID>
                    </BuyerParty>
                    <SellerParty>
                            <ID schemeID="EAN">5790022274291</ID>
                    </SellerParty>
                    <TaxTotal>
                            <CategoryTotal>
                                    <RateCategoryCodeID>VAT</RateCategoryCodeID>
                                    <RatePercentNumeric>25</RatePercentNumeric>
                                    <TaxAmounts>
                                            <TaxableAmount>2010.1</TaxableAmount>
                                            <TaxAmount>502.53</TaxAmount>
                                    </TaxAmounts>
                            </CategoryTotal>
                    </TaxTotal>
                    <LegalTotals>
                            <LineExtensionTotalAmount>1775</LineExtensionTotalAmount>
                            <ToBePaidTotalAmount>2512.63</ToBePaidTotalAmount>
                    </LegalTotals>
            </Invoice>
        '''

    def create_element(self, elem, deptor, test):

        self.verify_elem(elem, deptor)
        logger.info('Converting element: {}, {}'.format(elem, deptor))

        header = etree.fromstring(self.template.encode('utf-8'))
        header.find('ID').text = str(elem['key'])
        posting_date = elem['posting_date']
        if type(posting_date) is str or type(posting_date) is unicode:
            header.find('IssueDate').text = posting_date.split('T')[0]
        else:
            header.find('IssueDate').text = posting_date.isoformat().split('T')[0]

        if test or config.test_edi:
            pie_type = 'PIETEST'
        else:
            pie_type = 'PIE'

        header.find('TypeCode').text = pie_type
        #if fak.type == 'faktura':
        #else:
            #header.find('TypeCode').text = 'PCMTEST'

        ean = deptor['gln']

        header.find('BuyerParty').find('ID').text = ean
        header.find('BuyersReferenceID').text = ean
        header.find('ReferencedOrder').find('BuyersOrderID').text = elem['customer_order_number']
        header.find('SellerParty').find('ID').text = config.trade_ean
        tax = header.find('TaxTotal').find('CategoryTotal').find('TaxAmounts')

        total_without_tax = 0
        total_with_tax = 0

        for n, i in enumerate(elem['lines']):
            self.validate_line(i)
            item = etree.fromstring(self.i_line)
            item.find('ID').text = str(n+1)
            item.find('InvoicedQuantity').text = str(i['quantity'])
            item.find('LineExtensionAmount').text = "{0:.2f}".format(int(i['total_without_tax'])/100.00)
            item.find('BasePrice').find('PriceAmount').text = "{0:.2f}".format(int(i['price'])/100.00)
            item.find('Item').find('ID').text = i['gln_number']
            item.find('Item').find('Description').text = i['info']
            header.append(item)
            total_without_tax += int(i['total_without_tax'])
            total_with_tax += int(i['total_with_tax'])

        t_wo_t = "{0:.2f}".format(total_without_tax/100.00)
        t_w_t = "{0:.2f}".format(total_with_tax/100.00)
        tax.find('TaxableAmount').text = t_wo_t
        tax.find('TaxAmount').text = "{0:.2f}".format((total_with_tax - total_without_tax)/100.00)

        header.find('LegalTotals').find('LineExtensionTotalAmount').text = t_wo_t
        header.find('LegalTotals').find('ToBePaidTotalAmount').text = t_w_t

        temp = tempfile.TemporaryFile()
        temp.write(etree.tostring(header, encoding='utf-8'))
        temp.seek(0)

        return temp

class EDI(Exporter):

    def __init__(self):
        self.additions = 0

    def create_element(self, elem, deptor, test):
        self.verify_elem(elem, deptor)
        logger.info('Converting element: {}, {}'.format(elem, deptor))
        self.additions = 0
        #betaling = fak.dato + dt.timedelta(days=14)

        self.i_text = ''
        def add(text, *args):
            self.additions += 1
            self.i_text += text.format(*args) + "'\n"

        supergros_gln = "5790000000852"
        supergros_inv_reciever = "5790000004072"

        now = datetime.now()
        uuid = int(time.time())
        if test or config.test_edi:
            test = 1 # 1 = test, 0 = prod
        else:
            test = 0
        add("UNA:+.? ")
        add("UNB+UNOC:3+{}:14+{}:14+{}:{}+{}++++0++{}", config.trade_ean, supergros_gln, now.strftime('%y%m%d'), now.strftime('%H%M'), uuid, test)
        add("UNH+{}+INVOIC:D:96A:UN:EAN008", uuid)
        add("BGM+380+{}+9", elem['key']) #380 faktura, 381 kreditnota
        add("DTM+137:{}:102", elem['posting_date'].split('T')[0].replace('-', ''))
        add("RFF+VN:{}", elem['customer_order_number'])

        add("RFF+AAU:{}", elem['key'])
        add("DTM+171:{}:102", elem['delivery_date'].split('T')[0].replace('-', ''))
        add("NAD+BY+{}::9", supergros_inv_reciever)
        add("NAD+SU+{}::9", config.trade_ean)
        add("NAD+DP+{}::9", deptor['gln'])
        add("NAD+IV+{}::9", supergros_gln)
        add("TAX+7+VAT::9+++:::25+S")
        add("CUX+2:DKK:4")
        total_without_tax = 0
        total_with_tax = 0
        line_number = 0
        for n, i in enumerate(elem['lines']):

            self.validate_line(i)
            line_number += 1
            add("LIN+{}++{}:EN", line_number, i['gln_number'])

            add("PIA+1+{}:SA", i['item_number'])
            #PIA+1+9996:GB' # buyers item group
            add("IMD+F++:::{}:", i['info'].encode('utf8'))

            add("QTY+47:{}:PK", i['quantity'])
            line_total = "{0:.2f}".format(int(i['total_without_tax'])/100.00)
            add("MOA+203:{}", line_total)
            price = "{0:.2f}".format(int(i['price'])/100.00)
            add("PRI+AAA:{}", price)

            total_without_tax += int(i['total_without_tax'])
            total_with_tax += int(i['total_with_tax'])

        t_wo_t = "{0:.2f}".format(total_without_tax/100.00)
        t_w_t = "{0:.2f}".format(total_with_tax/100.00)
        tax = "{0:.2f}".format((total_with_tax - total_without_tax)/100.00)

        add("UNS+S")
        add("CNT+2:{}", line_number)
        add("MOA+79:{}", t_wo_t)
        add("MOA+86:{}", t_w_t)
        add("MOA+125:{}", t_wo_t)
        add("MOA+176:{}", tax)
        add("TAX+7+VAT::9+++:::25++S")
        add("UNT+{}+{}", self.additions - 1, uuid)
        add("UNZ+1+{}", uuid)

        temp = tempfile.TemporaryFile()
        temp.write(self.i_text)
        temp.seek(0)

        return temp
