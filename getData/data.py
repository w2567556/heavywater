# create data generator
class csvStream(object):
    def __init__(self,path):
        self.path=path
    def __iter__(self):
        with open(self.path, 'r') as csv:
            for line in csv:
                text = line[:-1]
                index = 0
                try:
                    while (line[index].isupper()) or (line[index] == ' ') or (line[index] == ',') or (line[index] == '-') :
                        text = text[1:]
                        index = index + 1
                except:
                    pass
                label = line[:index-1]
                feature = text.split(' ')
                #if feature[0] == '':
                    #continue
                yield  label,feature
