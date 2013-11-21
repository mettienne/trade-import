# -*- coding: utf-8 -*-
import os
import config
import tempfile
import xml.etree.ElementTree as etree

class OIOXML():

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

        self.ean_list = {}

        # read provided config file from edi
        # very dansk supermarked specific and to be moved
        with open(os.path.join(config.data_path, 'butik.csv')) as f:
            for l in f.readlines():
                    res = l.split(';')
                    if len(res) != 10:
                        print 'warning'
                    self.ean_list[res[0]] = res[9]

    def create_element(self, elem, edi):

        if elem['customer_order_number'].strip():
            kundeordrenummer = elem['customer_order_number']
        else:
            raise Exception('Kundeordrenummer mangler på faktura {}'.format(elem['key']))
        if not edi in self.ean_list:
            raise Exception('Kunde ean-nummer matcher ikke DanskSupermarked på faktura {}'.format(elem['key']))


        header = etree.fromstring(self.template.encode('utf-8'))
        header.find('ID').text = str(elem['key'])
        posting_date = elem['posting_date']
        if type(posting_date) is str or type(posting_date) is unicode:
            header.find('IssueDate').text = posting_date.split('T')[0]
        else:
            header.find('IssueDate').text = posting_date.isoformat().split('T')[0]

        if 'test' in elem and  elem['test']:
            header.find('TypeCode').text = 'PIETEST'
        else:
            header.find('TypeCode').text = 'PIE'

        #if fak.type == 'faktura':
        #else:
            #header.find('TypeCode').text = 'PCMTEST'

        ean = self.ean_list[edi]

        header.find('BuyerParty').find('ID').text = ean
        header.find('BuyersReferenceID').text = ean
        header.find('ReferencedOrder').find('BuyersOrderID').text = kundeordrenummer

        header.find('SellerParty').find('ID').text = config.trade_ean
        tax = header.find('TaxTotal').find('CategoryTotal').find('TaxAmounts')

        total_without_tax = 0
        total_with_tax = 0

        for n, i in enumerate(elem['lines']):
            if int(i['total_without_tax'])/100.00 == 0:
                continue
            item = etree.fromstring(self.i_line)
            item.find('ID').text = str(n+1)
            item.find('InvoicedQuantity').text = str(i['quantity'])
            item.find('LineExtensionAmount').text = "{0:.2f}".format(int(i['total_without_tax'])/100.00)
            item.find('BasePrice').find('PriceAmount').text = "{0:.2f}".format(int(i['price'])/100.00)
            item_ean = i['ean']
            if not item_ean.isdigit():
                raise Exception('Ean-nummer mangler på vare {}'.format(i['item_number']))
            item.find('Item').find('ID').text = item_ean
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
