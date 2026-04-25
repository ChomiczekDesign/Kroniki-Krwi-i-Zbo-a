# Walka

W **Genesys** walka jest rozgrywana w turach i rundach. Każda runda obejmuje moment działania wszystkich uczestników starcia, a każda tura opisuje to, co w tym czasie robi jedna postać lub przeciwnik.

System nie próbuje symulować każdego ruchu co do sekundy. Zamiast tego walka opiera się na prostych, powtarzalnych elementach: kolejności inicjatywy, wykonywaniu akcji i manewrów, testach ataku oraz interpretacji symboli na kościach.

## Runda i tura

Walka toczy się w kolejnych **rundach**. W każdej rundzie wszyscy uczestnicy mają okazję działać.

Kiedy przychodzi kolej postaci, wykonuje ona swoją **turę**. W swojej turze postać może zwykle wykonać:
- **1 akcję**
- **1 manewr**
- Dodatkowy, **2 manewr** kosztujeący **2 straina**.

## Inicjatywa

Na początku starcia ustalana jest kolejność działania.
- **Cool** służy do inicjatywy, gdy konflikt jest spodziewany
- **Vigilance** służy do inicjatywy, gdy konflikt zaczyna się nagle albo z zaskoczenia

Dodatkowe zasady:
- **#Triumph** pozwala wykonać **1 dodatkowy manewr w pierwszej rundzie starcia**,
- **#Despair** powoduje utratę **1 manewru w pierwszej rundzie starcia**.

## Typy działań w walce

W swojej turze postać wykonuje różne typy działań.

### Akcja

**Akcja** to główne działanie postaci w turze. W walce najczęściej będzie to:
- wykonanie ataku,
- użycie zdolności,
- rzucenie zaklęcia,
- wykonanie testu umiejętności,
- inne znaczące działanie wymagające testu.

Postać zwykle ma tylko **jedną akcję na turę**.

### Manewr

**Manewr** to krótsze, prostsze działanie wspierające akcję albo zmieniające pozycję postaci.

Typowe manewry w walce to:
- przemieszczenie się,
- wyciągnięcie albo schowanie broni,
- przycelowanie,
- zajęcie osłony,
- wstanie z ziemi albo padnięcie na ziemię,
- interakcja z otoczeniem,
- koncentracja, jeśli wymaga tego efekt.

Postać zwykle wykonuje **jeden manewr za darmo** w turze.  
Może wykonać **drugi manewr**, ale zazwyczaj kosztuje to **2 strainu**. Cheat sheet wymienia też typowe manewry, takie jak **Aim**, **Assist**, **Guarded Stance**, **Take Cover**, **Manage Gear** i **Move**. :contentReference[oaicite:2]{index=2}

### Incidental

**Incidental** to drobne działanie, które nie kosztuje ani akcji, ani manewru. W praktyce są to rzeczy szybkie i pomocnicze, które nie dominują tury.

Typowe przykłady:
- krótka wypowiedź,
- upuszczenie przedmiotu,
- puszczenie kogoś, kogo się trzyma,
- drobna zmiana pozycji,
- wychylenie się zza rogu.

### Out-of-Turn Incidental

Niektóre Incidentale mogą zostać wykonane **poza własną turą**. Są to tak zwane **Out-of-Turn Incidentals**.

Zwykle używa się ich do:
- bardzo krótkiej reakcji,
- wypowiedzi,
- drobnej czynności, która nie zmienia znacząco przebiegu sceny.
- aktywowania powązanego talentu

Ostateczna decyzja, czy coś może zostać wykonane jako **Out-of-Turn Incidental**, należy do MG.

## Atak

Aby wykonać atak, postać wybiera:
- odpowiedni cel,
- odpowiednią broń lub formę ataku,
- właściwą umiejętność.

Następnie buduje pulę kości zgodnie z zasadami testu:
- z cechy i umiejętności powstają kości pozytywne,
- MG dodaje trudność ataku,
- sytuacja może dodawać #Boost lub #Setback.

Jeśli po skasowaniu symboli w wyniku zostanie co najmniej **1 #Success**, atak trafia.

![[Zasięgi#Zasięg a broń]]

## Trafienie i obrażenia

- Udany atak oznacza, że cel został trafiony. Następnie wylicza się obrażenia.
- Zadawanie obrażeń:
  - **obrażenia broni + dodatkowe #Success = obrażenia zadane przed redukcją**
  - Następnie cel zmniejsza te obrażenia o **[[SOAK]]**.
  - Dopiero pozostała wartość zadaje **[[Wounds]]**.

## #Advantage i #Threat w walce

Walka w Genesys nie opiera się wyłącznie na pytaniu „trafił czy nie”. Bardzo ważne są także efekty poboczne wynikające z **#Advantage**, **#Threat**, **#Triumph** i **#Despair**

### Critical Injuries i qualities broni

Część wydatków #Advantage i #Triumph może też służyć do:
- aktywowania qualities broni,
- zadania **Critical Injury**: Jeśli broń ma **Critical Rating**, odpowiednia liczba #Advantage pozwala wywołać rzut na obrażenia krytyczne. 
- uruchomienia specjalnych efektów opisu broni.

![[Wykorzystanie Adventage i Threat w walce]]


